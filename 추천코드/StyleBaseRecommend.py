from typing import List
from fastapi import Body, FastAPI
from firebase_admin import credentials, initialize_app, storage
from domain import RecommendRequestDto
from img_path import load_closet, get_image_paths
from cloth_score import cal_clothes_score, calculate_similarity

def main(temperature, recommendDto: List[RecommendRequestDto]):
    #print("\n<스타일 목록>")
    #print("[FORMAL, MINIMALISTIC, CASUAL, STREET, SPORTS]")
    # dir_path="사용자1옷장"
    
    user_style = recommendDto[0].style
    base_dir_path = "스타일 코디 모음집/"+user_style+'/'    # 최신 트렌드 반영 모델 사진 (풀착장)

    closet = load_closet(recommendDto)
    suitable_clothes_by_temperature = cal_clothes_score(temperature,closet)

    if not (suitable_clothes_by_temperature["TOPS"] and suitable_clothes_by_temperature["BOTTOMS"]):
        print("현재 온도에 적합한 TOPS 또는 BOTTOMS가 없습니다.")
        return
    
    cloth_urls = {"TOPS":[cloth['img_url'] for cloth in suitable_clothes_by_temperature['TOPS']],
                         "BOTTOMS":[cloth['img_url'] for cloth in suitable_clothes_by_temperature['BOTTOMS']]}
    
    base_image_paths = get_image_paths(base_dir_path)

    result = calculate_similarity(base_image_paths, cloth_urls)
    return result



if __name__ == "__main__":
    main()

cred = credentials.Certificate("coordikitty-firebase-adminsdk-1ld5i-c4f40d3461.json")
initialize_app(cred, {
    'storageBucket': "coordikitty.appspot.com" 
})
bucket = storage.bucket()
app = FastAPI()
local_file_path = '1.png'

@app.post("/recommend")
async def categorization(recommendDto: List[RecommendRequestDto] = Body(...)):
    response = main(recommendDto[0].temperature, recommendDto)
    return response
	#BOTTOMS_LONG	BOTTOMS	CASUAL	NORMAL	https://firebasestorage.googleapis.com/v0/b/coordikitty.appspot.com/o/clothes%2F0b022f18-f1b5-48b1-a847-5f5b2550b7df%2F0b022f18-f1b5-48b1-a847-5f5b2550b7df?alt=media
	#TOPS_LONG	TOPS	CASUAL	S_THIN	https://firebasestorage.googleapis.com/v0/b/coordikitty.appspot.com/o/clothes%2F144d4619-f9cc-4864-ae5f-2f571b3fea51%2F144d4619-f9cc-4864-ae5f-2f571b3fea51?alt=media
	#TOPS_LONG	TOPS	CASUAL	S_THICK	https://firebasestorage.googleapis.com/v0/b/coordikitty.appspot.com/o/clothes%2F4e6f60b6-eb51-43b2-adcf-95309d923b30%2F4e6f60b6-eb51-43b2-adcf-95309d923b30?alt=media
	#TOPS_LONG	TOPS	CASUAL	S_THICK	https://firebasestorage.googleapis.com/v0/b/coordikitty.appspot.com/o/clothes%2F6300265d-c8b2-484a-b6bc-53a04530888d%2F6300265d-c8b2-484a-b6bc-53a04530888d?alt=media
	#BOTTOMS_LONG	BOTTOMS	CASUAL	S_THIN	https://firebasestorage.googleapis.com/v0/b/coordikitty.appspot.com/o/clothes%2F733c1866-c1ea-4792-ae77-cea436409914%2F733c1866-c1ea-4792-ae77-cea436409914?alt=media