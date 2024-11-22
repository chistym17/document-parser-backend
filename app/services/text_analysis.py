from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import spacy

router = APIRouter()
nlp = spacy.load("en_core_web_sm")

class TextRequest(BaseModel):
    text: str

@router.post("/analyze")
async def analyze_text(request: TextRequest):
    doc = nlp(request.text)
    keywords = [token.text for token in doc if not token.is_stop and token.is_alpha]
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    
    return {"keywords": keywords, "entities": entities}
