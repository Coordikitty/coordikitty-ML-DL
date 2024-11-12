from pydantic import BaseModel
from torchvision.models import resnext101_64x4d
import torch
import torch.nn as nn

temperature_ranges_by_cloth = {
    "BOTTOMS_SHORT":{
        "THICK":[(23, 27), (28, float('inf'))],
        "S_THICK":[(23, 27), (28, float('inf'))],
        "NORMAL":[(23, 27), (28, float('inf'))],
        "S_THIN":[(23, 27), (28, float('inf'))],
        "THIN":[(23, 27), (28, float('inf'))]
    },
    "LESS":{
        "THICK":[(28, float('inf'))],
        "S_THICK":[(28, float('inf'))],
        "NORMAL":[(28, float('inf'))],
        "S_THIN":[(28, float('inf'))],
        "THIN":[(28, float('inf'))]
    },
    "TOPS_SHORT":{
        "THICK":[(20, 22)],
        "S_THICK":[(20, 22)],
        "NORMAL":[(20, 22)],
        "S_THIN":[(23, 27)],
        "THIN":[(23, 27)]
    },
    "BOTTOMS_LONG":{
        "THICK":[(9, 11)],
        "S_THICK":[(12, 16)],
        "NORMAL":[(20, 22), (17, 19)],
        "S_THIN":[(23, 27)],
        "THIN":[(28, float('inf'))]
    },
    "TOPS_LONG":{
        "THICK":[(5, 8)],
        "S_THICK":[(9, 11)],
        "NORMAL":[(12, 16)],
        "S_THIN":[(17, 19)],
        "THIN":[(20, 22)]
    }
}

temperature_range = [(28, float('inf')), (23, 27), (20, 22), (17, 19), (12, 16), (9, 11), (5, 8), (-float('inf'), 4)]

class RecommendRequestDto(BaseModel):
    clothImages: str
    temperature: int
    style: str
    large: str
    medium: str
    thickness: str

class RecommendGetResponseDto:
    def __init__(self, topImage, bottomImage):
        self.topImage = topImage
        self.bottomImage = bottomImage

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