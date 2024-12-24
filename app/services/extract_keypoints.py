from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from transformers import pipeline
import torch

router = APIRouter()

extractor = pipeline(
    "text2text-generation",
    model="facebook/bart-large-cnn", 
    device=0 if torch.cuda.is_available() else -1
)

class ExtractionRequest(BaseModel):
    text: str

@router.post("/extract-keywords")
async def extract_key_points(request: ExtractionRequest):
    try:
        text = request.text
        max_chunk_length = 1024
        chunks = [text[i:i + max_chunk_length] for i in range(0, len(text), max_chunk_length)]
        key_points = []

        prompt_template = "Extract key points from this text: {}"

        for chunk in chunks:
            formatted_prompt = prompt_template.format(chunk)
            result = extractor(
                formatted_prompt,
                max_length=150,
                min_length=30,
                do_sample=True,
                temperature=0.7,
                num_beams=4
            )
            key_points.append(result[0]['generated_text'])

        final_points = ' '.join(key_points)

        formatted_points = '\n'.join(
            f"• {point.strip()}" 
            for point in final_points.split('.')
            if point.strip()
        )

        return {
            "status": "success",
            "key_points": formatted_points
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting key points: {str(e)}"
        )