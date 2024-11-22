from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from app.services import text_analysis, text_extraction, text_categorization

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
db = client['document']

app.include_router(text_analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(text_extraction.router, prefix="/api/extraction", tags=["extraction"])
app.include_router(text_categorization.router, prefix="/api/categorization", tags=["categorization"])

@app.get("/")
def home():
    return {"message": "Welcome to the Backend Server!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
