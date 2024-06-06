import torch
from torchvision import models
import pandas as pd

from params import device, transform

중분류_pth = 'C:/Users/lhj30/OneDrive/4-1/MIDAS/model/model_resnet50_중분류.pth'
중분류_cvs = 'C:/Users/lhj30/OneDrive/4-1/MIDAS/model/중분류(데님,스웨트).csv'

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
    
    def predict_image_category_m(image):
        # image = Image.open(image_path)
        image = transform(image).unsqueeze(0).to(device)
        
        with torch.no_grad():
            outputs = model_m(image)
            _, predicted = torch.max(outputs, 1)
            predicted_idx = predicted.item()
            category = idx_to_class[predicted_idx]
        
        return category
    
    return predict_image_category_m

# 중분류
predict_image_category_m = medium_categorize()