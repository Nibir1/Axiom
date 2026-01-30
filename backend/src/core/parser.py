"""
parser.py
---------
Extracts raw text from binary file formats (PDF).
"""
import io
from pypdf import PdfReader
from fastapi import UploadFile

async def parse_pdf(file: UploadFile) -> str:
    """
    Reads a PDF file from memory and extracts text.
    """
    content = await file.read()
    stream = io.BytesIO(content)
    reader = PdfReader(stream)
    
    text = []
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text.append(extracted)
            
    return "\n".join(text)