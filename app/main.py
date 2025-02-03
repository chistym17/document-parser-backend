from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from app.services import text_extraction,image_extraction,link_extraction

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(text_extraction.router, prefix="/api/extraction", tags=["extraction"])
app.include_router(image_extraction.router, prefix="/api/extraction", tags=["images"])
app.include_router(link_extraction.router, prefix="/api/extraction", tags=["links"])

@app.get("/")
def home():
    return {"message": "Welcome to the Backend Server!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

