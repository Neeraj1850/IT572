from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from tensorflow.keras.applications.vgg16 import preprocess_input
import numpy as np
from PIL import Image
import re
from io import BytesIO
import uvicorn
import asyncpg
import pytesseract
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use environment variables
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')
DATABASE_NAME = os.getenv('DATABASE_NAME')
TESSERACT_CMD = os.getenv('TESSERACT_CMD')
MODEL_PATH = os.getenv('MODEL_PATH')
CORS_ORIGIN = os.getenv('CORS_ORIGIN')
UNIT_COST_PER_KWH = float(os.getenv('UNIT_COST_PER_KWH', 0.33))

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

model = None

app = FastAPI()

origins = [
    CORS_ORIGIN, 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True, 
    allow_methods=["*"],  
    allow_headers=["*"], 
)

async def create_db_pool():
    return await asyncpg.create_pool(
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        database=DATABASE_NAME
    )

db_pool = None

@app.on_event("startup")
async def startup_event():
    global db_pool, model
    db_pool = await create_db_pool()
    model = load_model('./Model0.h5')  # Load your pre-trained model
    print("Database pool and model are ready")

APPLIANCE_TYPE_TO_TABLE = {
    'Air Conditioner': 'AirConditioner',
    'Washing Machine': 'WashingMachine',
    'Refrigerator': 'Refrigerator',
    'Oven': 'Oven',
    'Dish Washer': 'DishWasher'
}

from fastapi import HTTPException

@app.get("/appliances/{appliance_type}")
async def fetch_appliance_data(appliance_type: str, page: int = 1):
    limit = 10
    offset = (page - 1) * limit

    table_name = APPLIANCE_TYPE_TO_TABLE.get(appliance_type)

    if not table_name:
        raise HTTPException(status_code=400, detail="Invalid appliance type")

    async with db_pool.acquire() as connection:
        try:
            query = f"""
                SELECT model_num, brand_name, aec 
                FROM {table_name}
                LIMIT $1 OFFSET $2;
            """
            result = await connection.fetch(query, limit, offset)

            if result:
                return [dict(record) for record in result]
            else:
                return []
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching appliances: {str(e)}")


@app.post("/upload/")
async def create_upload_file(energy_sticker: UploadFile = None, appliance_photo: UploadFile = File(...)):
    kwh_value = None

    # Check if the appliance photo is provided
    if not appliance_photo.filename:
        raise HTTPException(status_code=400, detail="Appliance photo file is required.")

    # If energy sticker is provided, process it
    if energy_sticker and energy_sticker.filename:
        try:
            contents = await energy_sticker.read()
            image = Image.open(BytesIO(contents))
            kwh_value = extract_largest_kwh_value(image)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process energy sticker: {str(e)}")
    
    # Process the appliance photo and predict the class
    try:
        contents_appliance_photo = await appliance_photo.read()
        image_appliance_photo = Image.open(BytesIO(contents_appliance_photo))
        predicted_class = predict_appliance_class(image_appliance_photo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process appliance photo: {str(e)}")

    # If energy sticker not provided, lookup UEC value for predicted appliance in database
    if kwh_value is None:
        try:
            async with db_pool.acquire() as connection:
                uec_result = await connection.fetchrow(
                    "SELECT uec FROM average_appliance_EC WHERE appliance = $1", predicted_class
                )
                if uec_result:
                    kwh_value = uec_result['uec']
                    print(kwh_value)
                else:
                    raise HTTPException(status_code=404, detail="Appliance not found in database")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching UEC from database: {str(e)}")
    
    try:
        appliances = await fetch_appliances_consuming_less_than(kwh_value, predicted_class)
        total_cost = "Not calculated"
        if kwh_value is not None:
            total_cost = calculate_cost(kwh_value, 0.33)  # Assuming 0.33 is the unit cost per kWh
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching appliances: {str(e)}")

    return {"totalCost": total_cost, "appliances": appliances, "predictedClass": predicted_class}


async def fetch_appliances_consuming_less_than(kwh_value, appliance_type):
    async with db_pool.acquire() as connection:
        # Safely get the table name from the appliance type
        table_name = APPLIANCE_TYPE_TO_TABLE.get(appliance_type)

        # If the table name is not found in the map, it's an invalid type
        if not table_name:
            raise HTTPException(status_code=400, detail="Invalid appliance type")

        query = f"""
            SELECT model_num, brand_name, aec 
            FROM {table_name}
            WHERE aec < $1
            ORDER BY aec ASC
            LIMIT 5;
        """

        try:
            result = await connection.fetch(query, kwh_value)
            if result:
                return [dict(record) for record in result]
            else:
                return []
        except Exception as e:
            raise HTTPException(status_code=500, detail={str(e)})


def extract_largest_kwh_value(image):
    text = pytesseract.image_to_string(image, lang='eng')
    kwh_values = re.findall(r'(\d+)\s*kWh', text)
    kwh_numbers = [int(value) for value in kwh_values]
    return max(kwh_numbers) if kwh_numbers else None

def calculate_cost(kwh, unit_cost):
    return round(float(kwh) * unit_cost, 2)

class_names = ['Air Conditioner', 'Dish Washer', 'Oven', 'Refrigerator', 'Washing Machine']

def predict_appliance_class(image):
    # Resize the image to the model's expected input size
    image_resized = image.resize((224, 224))

    # Convert the resized PIL Image to a Numpy array and preprocess
    img_array = img_to_array(image_resized)
    img_batch = np.expand_dims(img_array, axis=0)  # Add batch dimension for the model
    img_preprocessed = preprocess_input(img_batch)  # Preprocess the image
    
    # Make prediction
    predictions = model.predict(img_preprocessed)
    predicted_index = np.argmax(predictions, axis=1)[0]  # Get the index of the highest probability
    # Map the predicted index to the corresponding class name
    predicted_class_name = class_names[predicted_index]
    return predicted_class_name

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
