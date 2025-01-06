from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
import fitz  # PyMuPDF
import os
import shutil
import re
from typing import List, Optional
from urllib.parse import urlparse

router = APIRouter()
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}

class ExtractedLink(BaseModel):
    url: str
    page_number: Optional[int] = None
    is_valid: bool
    context: Optional[str] = None

class TextLinkRequest(BaseModel):
    text: str

def is_allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def extract_urls_from_text(text: str) -> List[str]:
    url_pattern = r"""
        ((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|
        (?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))
        (?::\d+)?(?:/[^\s]*)?)|
        ((?:www\.)(?:[\da-z\.-]+)\.(?:[a-z]{2,6})(?:/[^\s]*)?)
    """
    urls = re.finditer(url_pattern, text, re.VERBOSE)
    return [url.group() for url in urls]

def extract_links_from_pdf(file_path: str) -> List[ExtractedLink]:
    extracted_links = []
    pdf_document = fitz.open(file_path)
    
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text = page.get_text()
        urls = extract_urls_from_text(text)
        
        for url in urls:
            url_pos = text.find(url)
            start_pos = max(0, url_pos - 50)
            end_pos = min(len(text), url_pos + len(url) + 50)
            context = text[start_pos:end_pos].strip()
            
            extracted_links.append(
                ExtractedLink(
                    url=url,
                    page_number=page_num + 1,
                    is_valid=is_valid_url(url),
                    context=context
                )
            )
    
    return extracted_links

def process_extracted_links(links: List[ExtractedLink]):
    valid_links = [link for link in links if link.is_valid]
    invalid_links = [link for link in links if not link.is_valid]
    
    return {
        "status": "success",
        "total_links_found": len(links),
        "valid_links_count": len(valid_links),
        "invalid_links_count": len(invalid_links),
        "valid_links": [link.dict() for link in valid_links],
        "invalid_links": [link.dict() for link in invalid_links]
    }

@router.post("/extract-links-from-file")
async def extract_links_from_file(file: UploadFile = File(...)):
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
            if filename.lower().endswith('.pdf'):
                links = extract_links_from_pdf(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                urls = extract_urls_from_text(text)
                links = [
                    ExtractedLink(
                        url=url,
                        is_valid=is_valid_url(url),
                        context=text[max(0, text.find(url)-50):text.find(url)+len(url)+50].strip()
                    ) 
                    for url in urls
                ]
            
            os.remove(file_path)
            
            result = process_extracted_links(links)
            result["filename"] = filename
            return result
            
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=500,
                detail=f"Link extraction failed: {str(e)}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

@router.post("/extract-links-from-text")
async def extract_links_from_text(request: TextLinkRequest):
    try:
        urls = extract_urls_from_text(request.text)
        links = [
            ExtractedLink(
                url=url,
                is_valid=is_valid_url(url),
                context=request.text[
                    max(0, request.text.find(url)-50):
                    request.text.find(url)+len(url)+50
                ].strip()
            ) 
            for url in urls
        ]
        
        return process_extracted_links(links)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting links from text: {str(e)}"
        ) 