from fastapi import Body, FastAPI
from fastapi import FastAPI, UploadFile, Body

from PIL import Image
import io

from small_categorize import predict_image_category_s
from medium_categorize import predict_image_category_m

from 스타일기반연결코드 import RecommendRequestDto, main

from typing import List

# server on
app = FastAPI()

@app.post("/categorization")
async def categorization(file: UploadFile):
    answer = {'large':"BOTTOMS"}
    
    img = Image.open(io.BytesIO(await file.read()))
    
    predicted_category_m = predict_image_category_m(img)
    predicted_category_s = predict_image_category_s(img)

    if predicted_category_m == 0:
        answer['medium'] = 'BOTTOMS_LONG'    
    elif predicted_category_m == 1:
        answer['medium'] = 'BOTTOMS_SHORT'        
    
    if predicted_category_s == 0:
        answer['samll'] = answer['medium'] + '_DENIM'
    elif predicted_category_s == 1:
        answer['samll'] = answer['medium'] + '_SWEAT'
    
        
    answer['fit'] = 'SKINNY'
    answer['gender'] = 'MALE'
    answer['style'] = 'FORMAL'

    return answer

@app.post("/recommend")
async def categorization(recommendDto: List[RecommendRequestDto] = Body(...)):
    response = main(recommendDto[0].temperature, recommendDto)
    return response

# uvicorn test:app --reload