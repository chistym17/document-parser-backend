from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import re
from typing import List, Optional
from urllib.parse import urlparse

router = APIRouter()

class ExtractedLink(BaseModel):
    url: str
    is_valid: bool
    context: Optional[str] = None

class TextLinkRequest(BaseModel):
    text: str

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

@router.post("/extract-links")
async def extract_links_from_text(request: TextLinkRequest):
    try:
        urls = extract_urls_from_text(request.text)
        
        links = []
        for url in urls:
            url_pos = request.text.find(url)
            start_pos = max(0, url_pos - 50)
            end_pos = min(len(request.text), url_pos + len(url) + 50)
            context = request.text[start_pos:end_pos].strip()
            
            links.append(
                ExtractedLink(
                    url=url,
                    is_valid=is_valid_url(url),
                    context=context
                )
            )

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
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting links from text: {str(e)}"
        ) 