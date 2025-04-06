from typing import List, Optional
from pydantic import BaseModel
import base64
import google
import requests
import json
import re
import datetime
import pypdfium2 as pdfium
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from uuid import uuid4
import tempfile
import aiofiles
import os
import pytesseract
import fitz  # PyMuPDF
import cv2
import numpy as np
from pdf2image import convert_from_path
from app.Config import ENV_PROJECT 
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

def get_date_now():
    return str(uuid4())

async def encode_image(image_path: str) -> str:
    async with aiofiles.open(image_path, "rb") as image_file:
        image_data = await image_file.read()
    return base64.b64encode(image_data).decode("utf-8")

# -----------------------------------------
# Gemini Client
# -----------------------------------------
# class GeminiClient:
#     def __init__(self):
#         self.api_key = ENV_PROJECT.GEMINI_API_KEY
#         genai.configure(api_key=ENV_PROJECT.GEMINI_API_KEY)
#         self.model = "gemini-pro"

#     async def pdf_to_images(self, pdf_path: str) -> List[str]:
#         pdf = pdfium.PdfDocument(pdf_path)
#         num_pages = len(pdf)
#         image_paths = []
#         for page_number in range(num_pages):
#             page = pdf[page_number]
#             bitmap = page.render(scale=2)
#             if bitmap is None:
#                 continue
#             pil_image = bitmap.to_pil()
#             image_path = f"/tmp/bill_page_{page_number + 1}.jpeg"
#             pil_image.save(image_path)
#             image_paths.append(image_path)
#         return image_paths

#     async def send_images_to_gemini(self, image_paths: List[str], prompt: str) -> dict:
#         try:
#             encoded_images = [await encode_image(img) for img in image_paths]
#             payload = {
#                 "model": self.model,
#                 "messages": [
#                     {"role": "user", "content": prompt},
#                     *[{"role": "user", "content": {"image": img}} for img in encoded_images]
#                 ],
#                 "max_tokens": 4096
#             }
#             response = requests.post(
#                 f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent",
#                 headers={"Authorization": f"Bearer {self.api_key}"},
#                 json=payload
#             )
#             if response.status_code != 200:
#                 raise HTTPException(status_code=response.status_code, detail="Gemini API request failed")
#             return response.json()
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Error processing images with Gemini: {e}")

# gemini= GeminiClient()