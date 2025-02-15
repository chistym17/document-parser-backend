from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
import os
import shutil
import pytesseract
from PIL import Image
from pdf2image import convert_from_path


pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/5/tessdata'

router = APIRouter()
UPLOAD_FOLDER = 'uploads'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff'}

def is_allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file_path: str) -> str:
    file_extension = file_path.split('.')[-1].lower()
    
    if file_extension == 'pdf':
        images = convert_from_path(file_path)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image) + "\n"
        return text
    else:
        return pytesseract.image_to_string(Image.open(file_path))

@router.post("/upload-and-extract")
async def upload_and_extract_file(file: UploadFile = File(...)):
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    try:
        filename = file.filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        try:
            text = extract_text_from_file(file_path)
            
            return {
                "status": "success",
                "filename": filename,
                "message": "File uploaded and text extracted successfully",
                "text": text
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"File uploaded but text extraction failed: {str(e)}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error uploading file: {str(e)}"
        )
