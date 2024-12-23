from transformers import pipeline
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()
sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

class SentimentRequest(BaseModel):
    text: str

@router.post("/analyze-sentiment")
async def analyze_sentiment(request: SentimentRequest):
    try:
        result = sentiment_analyzer(request.text)
        
        score = int(result[0]['label'].split()[0])
        sentiment_category = {
            1: "Very Negative",
            2: "Negative",
            3: "Neutral",
            4: "Positive",
            5: "Very Positive"
        }[score]

        return {
            "status": "success",
            "sentiment": sentiment_category,
            "score": score,
            "confidence": result[0]['score']
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing sentiment: {str(e)}"
        )