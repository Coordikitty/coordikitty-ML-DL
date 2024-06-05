from fastapi import FastAPI, UploadFile

from PIL import Image
import io

from small_categorize import predict_image_category_s
from medium_categorize import predict_image_category_m

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
        answer['samll'] = 'BOTTOMS_LONG_DENIM'
    elif predicted_category_s == 1:
        answer['samll'] =  'BOTTOMS_LONG_SWEAT'
        
    answer['fit'] = 'SKINNY'
    answer['gender'] = 'MALE'
    answer['style'] = 'FORMAL'

    return answer


# uvicorn test:app --reload