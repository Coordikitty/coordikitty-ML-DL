import torchvision.transforms as transforms
import numpy as np
from io import BytesIO
import requests
from PIL import Image
import torch

#GPU설정
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# YOLOv5 모델 로드
yolo_model = torch.hub.load('ultralytics/yolov5', 'custom', path="상하의_detection_yolov5s.pt")
yolo_model.to(device).eval()

# 이미지에서 사람 탐지 및 TOPS/BOTTOMS 추출
def detect_and_extract(image, conf_threshold=0.5):
    image_np = np.array(image)
    results = yolo_model(image_np)
    
    clothes_images = []
    
    for detection in results.xyxy[0]:
        x1, y1, x2, y2, conf, cls = detection
        if conf > conf_threshold:  # 사람 클래스
            if cls == 1:  # top 클래스
                top_image = image.crop((int(x1), int(y1), int(x2), int(y2)))
                clothes_images.append((top_image,'TOPS'))
            elif cls == 2:  # bottom 클래스
                bottom_image = image.crop((int(x1), int(y1), int(x2), int(y2)))
                clothes_images.append((bottom_image,'BOTTOMS'))
    print(clothes_images)
    return clothes_images

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

def preprocess_image(img_url):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    image_data = BytesIO(requests.get(img_url).content)

    image = Image.open(image_data).convert('RGB') #파이어베이스 url 접근으로 수정
    image=transform(image).unsqueeze(0)

    return image