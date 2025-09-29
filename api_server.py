from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from typing import Dict, Any

app = FastAPI(title="Cotton Disease Detection API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prediction data model
class PredictionData(BaseModel):
    disease: str
    confidence: float
    sprinkle: bool
    advice_en: str
    advice_hi: str
    pesticide_en: str
    pesticide_hi: str
    timestamp: str

# Store predictions
predictions = []

@app.post("/api/prediction")
async def receive_prediction(prediction: PredictionData):
    """Receive prediction from Raspberry Pi"""
    predictions.append(prediction.dict())
    return {"status": "success", "message": "Prediction received"}

@app.get("/api/predictions")
async def get_predictions():
    """Get all predictions"""
    return {"predictions": predictions}

@app.get("/api/latest")
async def get_latest_prediction():
    """Get the latest prediction"""
    if predictions:
        return predictions[-1]
    return {"message": "No predictions available"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
