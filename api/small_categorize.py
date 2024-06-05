import torch
from torchvision import models
import pandas as pd

from params import device_, transform

소분류_pth = 'C:/Users/lhj30/OneDrive/4-1/MIDAS/model/model_resnet50_소분류.pth'
소분류_cvs = 'C:/Users/lhj30/OneDrive/4-1/MIDAS/model/소분류(데님,스웨트).csv'

# 모델_소분류
def small_categorize():
    # 모델 정의 및 조정
    model_s = models.resnet50(weights=False)
    num_ftrs = model_s.fc.in_features
    model_s.fc = torch.nn.Linear(num_ftrs, 3)  # 체크포인트와 일치하도록 클래스 수를 3으로 변경
    model_s = model_s.to(device_)

    # 모델 로드
    checkpoint_path = 소분류_pth
    checkpoint = torch.load(checkpoint_path, map_location=device_)
    model_s.load_state_dict(checkpoint['model_state_dict'])
    model_s.eval()

    # 라벨 인덱스를 small_category로 매핑
    dfs = pd.read_csv(소분류_cvs)
    class_names = dfs['small_category'].unique()
    class_names = sorted(class_names, key=lambda x: list(dfs['small_category']).index(x))
    idx_to_class = {i: class_name for i, class_name in enumerate(class_names)}

    def predict_image_category_s(image):
        # image = Image.open(image_path)
        image = transform(image).unsqueeze(0).to(device_)
        
        with torch.no_grad():
            outputs = model_s(image)
            _, predicted = torch.max(outputs, 1)
            predicted_idx = predicted.item()
            category = idx_to_class[predicted_idx]
        
        return category
    
    return predict_image_category_s

# 소분류
predict_image_category_s = small_categorize()