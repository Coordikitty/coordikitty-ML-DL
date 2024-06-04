import numpy as np
import os
import json
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import resnext101_64x4d
from PIL import Image

#GPU설정
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# YOLOv5 모델 로드
yolo_model = torch.hub.load('ultralytics/yolov5', 'custom', path="상하의분리모델/상하의_detection_yolov5s.pt")
yolo_model.to(device).eval()

temperature_ranges_by_cloth = {
    "숏팬츠":{
        "매우 두꺼움":[(23, 27), (28, float('inf'))],
        "두꺼움":[(23, 27), (28, float('inf'))],
        "보통":[(23, 27), (28, float('inf'))],
        "얇음":[(23, 27), (28, float('inf'))],
        "매우 얇음":[(23, 27), (28, float('inf'))]
    },
    "민소매":{
        "매우 두꺼움":[(28, float('inf'))],
        "두꺼움":[(28, float('inf'))],
        "보통":[(28, float('inf'))],
        "얇음":[(28, float('inf'))],
        "매우 얇음":[(28, float('inf'))]
    },
    "반팔":{
        "매우 두꺼움":[(20, 22)],
        "두꺼움":[(20, 22)],
        "보통":[(20, 22)],
        "얇음":[(23, 27)],
        "매우 얇음":[(23, 27)]
    },
    "롱팬츠":{
        "매우 두꺼움":[(9, 11)],
        "두꺼움":[(12, 16)],
        "보통":[(20, 22), (17, 19)],
        "얇음":[(23, 27)],
        "매우 얇음":[(28, float('inf'))]
    },
    "긴팔":{
        "매우 두꺼움":[(5, 8)],
        "두꺼움":[(9, 11)],
        "보통":[(12, 16)],
        "얇음":[(17, 19)],
        "매우 얇음":[(20, 22)]
    }
}

temperature_range=[(28, float('inf')), (23, 27), (20, 22), (17, 19), (12, 16), (9, 11), (5, 8), (-float('inf'), 4)]

def load_closet(dir_path):
    closet = {"상의":[],"하의":[]}
    json_files = [pos_json for pos_json in os.listdir(dir_path) if pos_json.endswith('.json')]
    for json_file in json_files:
        file_path = os.path.join(dir_path, json_file)
        with open(file_path,'r',encoding='utf-8') as file:
            json_data = json.load(file)
            large_category, extracted_data = extract_data_from_json(json_data)
            closet[large_category].append(extracted_data)
    return closet

def extract_data_from_json(json_data):
    # 필요한 데이터만 추출하여 딕셔너리로 저장
    
    large_category = json_data.get("large_category")

    extracted_data = {
        "file_name": json_data.get("file_name"),
        "medium_category": json_data.get("medium_category"),
        "small_category": json_data.get("small_category"),
        "thickness": json_data.get("thickness"),
        "major_style": json_data.get("major_style"),
        "minor_style": json_data.get("minor_style")
    }
    return large_category, extracted_data

def cal_clothes_score(temperature, closet): #옷 점수 계산
    appropriate_clothes = {"상의": [], "하의": []}
    clothes_score = {"상의":[],"하의":[]}
    temp_idx = 0
    for i in range(len(temperature_range)):
        if temperature_range[i][0]<=temperature<=temperature_range[i][1]:
            temp_idx=i
            break
    for category, clothes in closet.items():
        for cloth in clothes:
            score = -float('inf')
            for temp_range in temperature_ranges_by_cloth[cloth["medium_category"]][cloth["thickness"][0]]:
                score = max(score,-abs(temp_idx-temperature_range.index(temp_range)))
            if(score>=-2):
                appropriate_clothes[category].append(cloth)
                clothes_score[category].append(score)

    clothes_and_score_top = np.vstack((np.array(appropriate_clothes["상의"]),np.array(clothes_score["상의"])))
    clothes_and_score_bottom = np.vstack((np.array(appropriate_clothes["하의"]),np.array(clothes_score["하의"])))

    clothes_and_score_top = clothes_and_score_top[:,clothes_and_score_top[1].argsort()[::-1]]
    clothes_and_score_bottom = clothes_and_score_bottom[:,clothes_and_score_bottom[1].argsort()[::-1]]

    appropriate_clothes = {
        "상의": clothes_and_score_top[0].tolist(),
        "하의": clothes_and_score_bottom[0].tolist()
    }

    return appropriate_clothes

# 이미지 전처리 함수
def preprocess_base_image(image_path):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    image = Image.open(image_path).convert('RGB')
    top_bottom_image = detect_and_extract(image)
    images = []
    for image_ in top_bottom_image:
        images.append((transform(image_[0]).unsqueeze(0),image_[1]))
    return images

def preprocess_image(image_path):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    image = Image.open(image_path).convert('RGB')
    image=transform(image).unsqueeze(0)
    return image

# 디렉토리에서 이미지 경로 목록 가져오기
def get_image_paths(directory_path):
    valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    return [os.path.join(directory_path, f) for f in os.listdir(directory_path) if os.path.splitext(f)[1].lower() in valid_extensions]

# ResNet-50 모델을 이용한 특성 추출 클래스
class FeatureExtractor(nn.Module):
    def __init__(self):
        super(FeatureExtractor, self).__init__()
        self.model = resnext101_64x4d(pretrained=True)
        self.model = nn.Sequential(*list(self.model.children())[:-1])  # 마지막 분류 계층 제거

    def forward(self, x):
        with torch.no_grad():
            features = self.model(x)
        return features.view(features.size(0), -1)

# 이미지에서 사람 탐지 및 상의/하의 추출
def detect_and_extract(image, conf_threshold=0.5):
    image_np = np.array(image)
    results = yolo_model(image_np)
    
    clothes_images = []
    
    for detection in results.xyxy[0]:
        x1, y1, x2, y2, conf, cls = detection
        if conf > conf_threshold:  # 사람 클래스
            if cls == 1:  # top 클래스
                top_image = image.crop((int(x1), int(y1), int(x2), int(y2)))
                clothes_images.append((top_image,'상의'))
            elif cls == 2:  # bottom 클래스
                bottom_image = image.crop((int(x1), int(y1), int(x2), int(y2)))
                clothes_images.append((bottom_image,'하의'))
    
    return clothes_images

# 유사도 계산 및 상위 3개 결과 출력 함수
def calculate_similarity(base_dir_path, cloth_file_names, dir_path):
    model = FeatureExtractor().eval()
    base_images_path = get_image_paths(base_dir_path)
    base_images=[]
    for base_image_path in base_images_path:
        base_images.append(preprocess_base_image(base_image_path))

    base_features_list = []
    for base_image in base_images:
        temp=[]
        for image_ in base_image:
            temp.append((model(image_[0]),image_[1]))
        base_features_list.append(temp)

    cos = nn.CosineSimilarity(dim=1, eps=1e-6)
    top3_coordi=[]
    for base_features in base_features_list:
        top2_images_TNB={"상의":[],"하의":[]}
        for base_feature in base_features:
            similarity_scores = {}
            for cloth_file_name in cloth_file_names[base_feature[1]]:
                target_features = model(preprocess_image(dir_path+'/'+cloth_file_name))
                similarity = cos(base_feature[0],target_features).item()
                similarity_scores[cloth_file_name]=similarity
            
            for top_2_image in sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)[:2]:
                top2_images_TNB[base_feature[1]].append(top_2_image)
        
        top3_coordi_by_one_base=[]
        for top_2_top in top2_images_TNB["상의"]:
            for top_2_bottom in top2_images_TNB["하의"]:
                top3_coordi_by_one_base.append((top_2_top[0], top_2_bottom[0], (top_2_top[1]+top_2_bottom[1])/2 ))
        
        top3_coordi_by_one_base.sort(key=lambda x: x[-1], reverse=True)
        # for coordi_by_one_base in top3_coordi_by_one_base[:3]:
        # top3_coordi.extend(top3_coordi_by_one_base)
        top3_coordi.append(top3_coordi_by_one_base[0])

    top3_coordi.sort(key=lambda x: x[-1],reverse=True)
    for top_coordi in top3_coordi[:3]:
        print(f"추천 코디:{top_coordi[0]}, {top_coordi[1]} / 점수: {top_coordi[2]}")

def main():
    temperature = round(float(input("-현재 온도 입력: ")))
    print("\n<스타일 목록>")
    print("[캐주얼, 미니멀, 스트릿, 스포티, 포멀]")
    user_style = input("-스타일 선택: ")
    print()

    dir_path="비슷한_이미지_선별_모음"
    base_dir_path = "스타일 코디 모음집/"+user_style+'/'

    closet = load_closet(dir_path)
    suitable_clothes_by_temperature = cal_clothes_score(temperature,closet)

    if not (suitable_clothes_by_temperature["상의"] and suitable_clothes_by_temperature["하의"]):
        print("현재 온도에 적합한 상의 또는 하의가 없습니다.")
        return
    cloth_file_names = {"상의":[cloth['file_name'] for cloth in suitable_clothes_by_temperature['상의']],
                         "하의":[cloth['file_name'] for cloth in suitable_clothes_by_temperature['하의']]}
    
    calculate_similarity(base_dir_path, cloth_file_names, dir_path)

if __name__ == "__main__":
    main()