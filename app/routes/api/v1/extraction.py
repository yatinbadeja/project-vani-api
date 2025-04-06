from fastapi import APIRouter
from fastapi import UploadFile, File
from app.database.repositories.extraction import extraction_tools
extraction = APIRouter()

@extraction.post("/file/upload")
async def upload_file(file: UploadFile = File(...)):
    response = await extraction_tools.text_extraction_for_scanned_and_selectable_file_for_json_format_through_gemini(file)
    print(response)
    
    



