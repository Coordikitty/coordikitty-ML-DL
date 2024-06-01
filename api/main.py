from fastapi import FastAPI, UploadFile

import torch
from torchvision import transforms, models
import pandas as pd
from PIL import Image
import io

소분류_pth = 'C:/Users/lhj30/OneDrive/4-1/MIDAS/model/model_resnet50_소분류.pth'
중분류_pth = 'C:/Users/lhj30/OneDrive/4-1/MIDAS/model/model_resnet50_중분류.pth'

소분류_cvs = 'C:/Users/lhj30/OneDrive/4-1/MIDAS/model/소분류(데님,스웨트).csv'
중분류_cvs = 'C:/Users/lhj30/OneDrive/4-1/MIDAS/model/중분류(데님,스웨트).csv'

# CUDA
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 데이터 전처리
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.Lambda(lambda x: x.convert('RGB')),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# 모델_중분류
def medium_categorize():
    # 모델 정의 및 조정
    model_m = models.resnet50(weights=False)
    num_ftrs = model_m.fc.in_features
    model_m.fc = torch.nn.Linear(num_ftrs, 2)  
    model_m = model_m.to(device)

    # 모델 로드
    checkpoint_path = 중분류_pth
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model_m.load_state_dict(checkpoint['model_state_dict'])
    model_m.eval()

    # 라벨 인덱스를 medium_category로 매핑
    dfm = pd.read_csv(중분류_cvs)
    class_names = dfm['medium_category'].unique()
    class_names = sorted(class_names, key=lambda x: list(dfm['medium_category']).index(x))
    idx_to_class = {i: class_name for i, class_name in enumerate(class_names)}
    
    def predict_image_category_m(image, model_m, transform, device, idx_to_class):
        # image = Image.open(image_path)
        image = transform(image).unsqueeze(0).to(device)
        
        with torch.no_grad():
            outputs = model_m(image)
            _, predicted = torch.max(outputs, 1)
            predicted_idx = predicted.item()
            category = idx_to_class[predicted_idx]
        
        return category
    
    return predict_image_category_m, model_m, idx_to_class

# 모델_소분류
def small_categorize():
    # 모델 정의 및 조정
    model_s = models.resnet50(weights=False)
    num_ftrs = model_s.fc.in_features
    model_s.fc = torch.nn.Linear(num_ftrs, 3)  # 체크포인트와 일치하도록 클래스 수를 3으로 변경
    model_s = model_s.to(device)

    # 모델 로드
    checkpoint_path = 소분류_pth
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model_s.load_state_dict(checkpoint['model_state_dict'])
    model_s.eval()

    # 라벨 인덱스를 small_category로 매핑
    dfs = pd.read_csv(소분류_cvs)
    class_names = dfs['small_category'].unique()
    class_names = sorted(class_names, key=lambda x: list(dfs['small_category']).index(x))
    idx_to_class = {i: class_name for i, class_name in enumerate(class_names)}

    def predict_image_category_s(image, model_s, transform, device, idx_to_class):
        # image = Image.open(image_path)
        image = transform(image).unsqueeze(0).to(device)
        
        with torch.no_grad():
            outputs = model_s(image)
            _, predicted = torch.max(outputs, 1)
            predicted_idx = predicted.item()
            category = idx_to_class[predicted_idx]
        
        return category
    
    return predict_image_category_s, model_s, idx_to_class

# 중분류
predict_image_category_m, model_m, idx_to_class_m = medium_categorize()

# 소분류
predict_image_category_s, model_s, idx_to_class_s = small_categorize()

# server on
app = FastAPI()

@app.post("/categorization")
async def categorization(file: UploadFile):
    answer = {
        'large':"BOTTOMS"
    }
    
    img = Image.open(io.BytesIO(await file.read()))
    
    predicted_category_m = predict_image_category_m(img, model_m, transform, device, idx_to_class_m)
    predicted_category_s = predict_image_category_s(img, model_s, transform, device, idx_to_class_s)

    if predicted_category_m == 0:
        answer['medium'] = 'BOTTOMS_LONG'
    elif predicted_category_m == 1:
        answer['medium'] = 'BOTTOMS_SHORT'
        
    if predicted_category_s == 0:
        answer['samll'] = 'BOTTOMS_LONG_DENIM'
    elif predicted_category_s == 1:
        answer['samll'] =  'BOTTOMS_LONG_SWEAT'
        
    answer['fit'] = 'SKINNY'
    answer['gender'] = 'MALE'
    answer['style'] = 'FORMAL'

    return answer


# uvicorn main:app --reload