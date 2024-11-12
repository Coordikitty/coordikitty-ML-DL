from typing import List
import os
from domain import RecommendRequestDto

def load_closet(recommendDto: List[RecommendRequestDto]):
    closet = {"TOPS":[],"BOTTOMS":[]}
    for cloth_data in recommendDto:
        cloth = {
            "img_url": cloth_data.clothImages,
            "medium_category": cloth_data.medium,
            "thickness": cloth_data.thickness
        }
        closet[cloth_data.large].append(cloth)
    return closet

# 디렉토리에서 이미지 경로 목록 가져오기
def get_image_paths(directory_path):
    valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    return [os.path.join(directory_path, f) for f in os.listdir(directory_path) if os.path.splitext(f)[1].lower() in valid_extensions]

def get_dir_paths(directory_path):
    return [os.path.join(directory_path, d) for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]