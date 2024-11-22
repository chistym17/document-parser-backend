from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

router = APIRouter()

class TextListRequest(BaseModel):
    text: List[str]

@router.post("/categorize")
async def categorize(request: TextListRequest):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(request.text)

    kmeans = KMeans(n_clusters=2, random_state=42).fit(X)
    labels = kmeans.labels_

    return {"labels": labels.tolist()}

