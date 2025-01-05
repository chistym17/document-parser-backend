from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
import fitz  
import os
import shutil
from typing import List
from pydantic import BaseModel
import uuid

router = APIRouter()

UPLOAD_FOLDER = 'uploads'
IMAGE_OUTPUT_FOLDER = 'extracted_images'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMAGE_OUTPUT_FOLDER, exist_ok=True)

class ImageExtractionResponse(BaseModel):
    image_id: str
    page_number: int
    image_format: str
    size_bytes: int

def extract_images_from_pdf(pdf_path: str) -> List[ImageExtractionResponse]:
    extracted_images = []
    
    try:
        pdf_document = fitz.open(pdf_path)
        
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                
                if base_image:
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    image_id = str(uuid.uuid4())
                    image_filename = f"{image_id}.{image_ext}"
                    image_path = os.path.join(IMAGE_OUTPUT_FOLDER, image_filename)
                    
                    with open(image_path, "wb") as image_file:
                        image_file.write(image_bytes)
                    
                    image_info = ImageExtractionResponse(
                        image_id=image_id,
                        page_number=page_num + 1,
                        image_format=image_ext,
                        size_bytes=len(image_bytes)
                    )
                    extracted_images.append(image_info)
        
        return extracted_images
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting images: {str(e)}"
        )

@router.post("/extract-images")
async def extract_images(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    try:
        unique_filename = f"{str(uuid.uuid4())}.pdf"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        try:
            extracted_images = extract_images_from_pdf(file_path)
            
            os.remove(file_path)
            
            return {
                "status": "success",
                "message": f"Successfully extracted {len(extracted_images)} images",
                "images": [img.dict() for img in extracted_images]
            }
            
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=500,
                detail=f"Image extraction failed: {str(e)}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

@router.get("/get-image/{image_id}")
async def get_image(image_id: str):
    try:
        for filename in os.listdir(IMAGE_OUTPUT_FOLDER):
            if filename.startswith(image_id + '.'):
                image_path = os.path.join(IMAGE_OUTPUT_FOLDER, filename)
                return FileResponse(image_path)
        
        raise HTTPException(
            status_code=404,
            detail="Image not found"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving image: {str(e)}"
        )

@router.delete("/delete-image/{image_id}")
async def delete_image(image_id: str):
    try:
        for filename in os.listdir(IMAGE_OUTPUT_FOLDER):
            if filename.startswith(image_id + '.'):
                image_path = os.path.join(IMAGE_OUTPUT_FOLDER, filename)
                os.remove(image_path)
                return {
                    "status": "success",
                    "message": f"Image {image_id} deleted successfully"
                }
        
        raise HTTPException(
            status_code=404,
            detail="Image not found"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting image: {str(e)}"
        ) 