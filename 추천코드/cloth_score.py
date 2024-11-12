from domain import temperature_range, temperature_ranges_by_cloth, RecommendGetResponseDto, FeatureExtractor
import numpy as np
import torch.nn as nn
from img_processing import preprocess_base_image, preprocess_image

def cal_clothes_score(temperature, closet): #옷 점수 계산
    appropriate_clothes = {"TOPS": [], "BOTTOMS": []}
    clothes_score = {"TOPS":[],"BOTTOMS":[]}
    current_temperature_idx = 0
    for idx in range(len(temperature_range)):
        if temperature_range[idx][0]<=temperature<=temperature_range[idx][1]:
            current_temperature_idx=idx
            break
    for category, clothes in closet.items():
        for cloth in clothes:
            score = -float('inf')
            for temp_range in temperature_ranges_by_cloth[cloth["medium_category"]][cloth["thickness"]]:
                score = max(score,-abs(current_temperature_idx-temperature_range.index(temp_range)))
            if(score>=-1): #현재 온도, 적정 온도 차이
                appropriate_clothes[category].append(cloth)
                clothes_score[category].append(score)

    clothes_and_score_top = np.vstack((np.array(appropriate_clothes["TOPS"]),np.array(clothes_score["TOPS"])))
    clothes_and_score_bottom = np.vstack((np.array(appropriate_clothes["BOTTOMS"]),np.array(clothes_score["BOTTOMS"])))

    clothes_and_score_top = clothes_and_score_top[:,clothes_and_score_top[1].argsort()[::-1]]
    clothes_and_score_bottom = clothes_and_score_bottom[:,clothes_and_score_bottom[1].argsort()[::-1]]

    appropriate_clothes = {
        "TOPS": clothes_and_score_top[0].tolist(),
        "BOTTOMS": clothes_and_score_bottom[0].tolist()
    }

    return appropriate_clothes

# 유사도 계산 및 상위 3개 결과 출력 함수
def calculate_similarity(base_images_path, cloth_urls):
    model = FeatureExtractor().eval()
    base_images=[]
    for base_image_path in base_images_path:
        base_images.append(preprocess_base_image(base_image_path))

    base_features_list = []
    for base_image in base_images:
        temp=[]
        for image_ in base_image:
            temp.append((model(image_[0]),image_[1]))
        base_features_list.append(temp)

    clothes_features = {"TOPS":[],"BOTTOMS":[]}
    for cloth_url in cloth_urls["TOPS"]:
        clothes_features["TOPS"].append((model(preprocess_image(cloth_url)),cloth_url))
    for cloth_url in cloth_urls["BOTTOMS"]:
        clothes_features["BOTTOMS"].append((model(preprocess_image(cloth_url)),cloth_url))
    
    cos = nn.CosineSimilarity(dim=1, eps=1e-6)
    top3_coordi=[]
    for base_features in base_features_list:
        top2_images_TNB={"TOPS":[],"BOTTOMS":[]}
        for base_feature in base_features:
            similarity_scores = {}
            for target_feature in clothes_features[base_feature[1]]:
                similarity = cos(base_feature[0],target_feature[0]).item()
                similarity_scores[target_feature[1]]=similarity
            
            for top_2_image in sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)[:1]: #상하의 각각 유사도 top
                top2_images_TNB[base_feature[1]].append(top_2_image)
        
        top3_coordi_by_one_base=[]
        for top_2_top in top2_images_TNB["TOPS"]:
            for top_2_bottom in top2_images_TNB["BOTTOMS"]:
                top3_coordi_by_one_base.append((top_2_top[0], top_2_bottom[0], (top_2_top[1]+top_2_bottom[1])/2 ))
        
        top3_coordi_by_one_base.sort(key=lambda x: x[-1], reverse=True) #한 게시글 유사도 top
        # for coordi_by_one_base in top3_coordi_by_one_base[:3]:
        # top3_coordi.extend(top3_coordi_by_one_base)
        top3_coordi.append(top3_coordi_by_one_base[0])

    top3_coordi.sort(key=lambda x: x[-1],reverse=True) #전체 유사도 top
    
    response=[]
    for top_coordi in top3_coordi[:3]:
        coordi_data = RecommendGetResponseDto(top_coordi[0],top_coordi[1])
        # coordi_data.topImage = top_coordi[0]
        # coordi_data.bottomImage = top_coordi[1]
        response.append(coordi_data)
    return response