from transformers import pipeline
from fastapi import APIRouter, HTTPException

router=APIRouter()
summarizer=pipeline("summarization",model="facebook/bart-large-cnn")

@router.post("/summarize-text")
async def summarize_text(text:str):
    try:
        max_chunk_length=1024
        chunks = [text[i:i + max_chunk_length] for i in range(0, len(text), max_chunk_length)]
        summaries=[]

        for chunk in chunks:
            summary=summarizer(chunk,max_length=130,min_length=30,do_sample=False)
            summaries.append(summary[0]['summary_text'])

        final_summary = ' '.join(summaries)

        return{
            "status":"success",
            "summary":final_summary
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summary: {str(e)}"
        )


        