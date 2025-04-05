import json
import cv2
import fitz  # PyMuPDF
import numpy as np
import pytesseract
import tempfile
from uuid import uuid4
from pdf2image import convert_from_path
from app.Config import ENV_PROJECT
import google.generativeai as genai


class ExtractionTools:
    async def text_extraction_for_scanned_and_selectable_file_for_json_format_through_gemini(self, file):
        input_token = 0
        output_token = 0
        extracted_text = ""

        filename = file["filename"]
        text_file_name = str(uuid4()) + filename.split("/")[-1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file_content = file["content"]
            temp_file.write(temp_file_content)
            temp_file_path = temp_file.name

        docs = fitz.open(temp_file_path)
        for page_num in range(len(docs)):
            data = docs[page_num].get_text("text")
            extracted_text += data
        print(extracted_text)   

        '''if len(extracted_text) < 50:
            extracted_text = ""
            with open("./extract.txt", mode='w') as text_file:
                images = convert_from_path(temp_file_path)
                for i, image in enumerate(images):
                    image = np.array(image)
                    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    text = pytesseract.image_to_string(grey)
                    extracted_text += text
                    text_file.write(f"{text_file_name} - Page No {i + 1}\n\n")
                    text_file.write(text)
                    text_file.write("\n\n")'''

        prompt = f'''
        You are a billing parser that generates strictly JSON-formatted responses. Follow these strict guidelines:

        Output Format:
        {{
            "invoice_no": "string",
            "date": "string",
            "stokist": {{
                "name": "string",
                "address": {{
                    "street": "string",
                    "city": "string",
                    "state": "string",
                    "zip_code": "string"
                }},
                "phone": "string",
                "GSTIN": "string",
                "DL_No": "string"
            }},
            "chemist": {{
                "name": "string",
                "address": {{
                    "street": "string",
                    "city": "string",
                    "state": "string",
                    "zip_code": "string"
                }},
                "GSTIN": "string",
                "DL_No": "string"
            }},
            "items": [
                {{
                    "product_name": "string",
                    "pack": "string",
                    "batch": "string",
                    "HSN": "string",
                    "expiry": "YYYY-MM",
                    "quantity": "string",
                    "MRP": "string",
                    "GST_percent": "string",
                    "amount": "string"
                }}
            ],
            "totals": {{
                "subtotal": 0.0,
                "discount": 0.0,
                "SGST": 0.0,
                "CGST": 0.0,
                "GST_total": 0.0,
                "grand_total": 0.0,
                "outstanding_amount": 0.0
            }}
        }}
        Basic information from the documents to be extracted:

        stokist -> the supplier who sells the medicines.
        chemist -> the buyer who purchase the medicines.
        invoice number -> unique sequential code that is systematically assigned to invoices.
        date -> date of purchasing the medicines.
        items -> list or table of all medicines details.

        Stokist Details :
        name -> Name of the stokist.
        address -> Residential address of stokist.
        street -> Street address.
        city -> City name.
        state -> State name (abbreviation or full).
        zip_code -> Postal code.
        phone -> contact number of stockist.
        GSTIN -> 15-digit PAN-based number allotted to stokist.
        DL_NO -> Drug license number alloted to stokist.

        Chemist Details :
        name -> Name of the chemist.
        address -> Residential address of chemist.
        street -> Street address.
        city -> City name.
        state -> State name (abbreviation or full).
        zip_code -> Postal code.
        GSTIN -> 15-digit PAN-based number allotted to chemist.
        DL_NO -> Drug license number alloted to chemist.

        Item Details:
        subtotal -> The total cost of all items before applying any taxes or discounts.
        discount -> Any reduction applied to the subtotal before calculating tax.
        SGST -> The tax collected by the state government.
        CGST -> The tax collected by the central government.
        GST_total -> The sum of SGST and CGST.
        grand_total -> The final amount to be paid, including taxes.
        outstanding_amount -> The remaining balance the buyer still owes to the supplier.


        Input Text:
        {extracted_text}
        '''

        genai.configure(api_key=ENV_PROJECT.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-pro")

        response = model.generate_content(prompt)
        content = response.text.strip()

        if content.startswith("```json"):
            content = content[len("```json"):].strip()
        if content.endswith("```"):
            content = content[:-len("```")].strip()

        data = json.loads(content)
        data["token"] = {
            "input_token": input_token,  # Placeholder: replace with actual counting logic if need
        }

# -----------------------------------------
# Imports and Setup
# -----------------------------------------
from typing import List, Optional
from pydantic import BaseModel
import base64
import google.generativeai as genai
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
from app.Config import ENV_PROJECT  # You must configure your .env reader to set ENV_PROJECT.GEMINI_API_KEY

# Tesseract setup (for Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# -----------------------------------------
# Utility Functions
# -----------------------------------------
def get_date_now():
    return str(uuid4())

async def encode_image(image_path: str) -> str:
    async with aiofiles.open(image_path, "rb") as image_file:
        image_data = await image_file.read()
    return base64.b64encode(image_data).decode("utf-8")

# -----------------------------------------
# Gemini Client
# -----------------------------------------
class GeminiClient:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = model

    async def pdf_to_images(self, pdf_path: str) -> List[str]:
        pdf = pdfium.PdfDocument(pdf_path)
        num_pages = len(pdf)
        image_paths = []
        for page_number in range(num_pages):
            page = pdf[page_number]
            bitmap = page.render(scale=2)
            if bitmap is None:
                continue
            pil_image = bitmap.to_pil()
            image_path = f"/tmp/bill_page_{page_number + 1}.jpeg"
            pil_image.save(image_path)
            image_paths.append(image_path)
        return image_paths

    async def send_images_to_gemini(self, image_paths: List[str], prompt: str) -> dict:
        try:
            encoded_images = [await encode_image(img) for img in image_paths]
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt},
                    *[{"role": "user", "content": {"image": img}} for img in encoded_images]
                ],
                "max_tokens": 4096
            }
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload
            )
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Gemini API request failed")
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing images with Gemini: {e}")

# -----------------------------------------
# Pydantic Models for Validation
# -----------------------------------------
class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str

class Stokist(BaseModel):
    name: str
    address: Address
    phone: str
    GSTIN: str
    DL_No: str

class Chemist(BaseModel):
    name: str
    address: Address
    GSTIN: str
    DL_No: str

class Item(BaseModel):
    product_name: str
    pack: str
    batch: str
    HSN: str
    expiry: str
    quantity: str
    MRP: str
    GST_percent: str
    amount: str

class Totals(BaseModel):
    subtotal: float
    discount: float
    SGST: float
    CGST: float
    GST_total: float
    grand_total: float
    outstanding_amount: float

class BillingData(BaseModel):
    invoice_no: str
    date: str
    stokist: Stokist
    chemist: Chemist
    items: List[Item]
    totals: Totals
    input_token: Optional[int] = None
    output_token: Optional[int] = None

# -----------------------------------------
# Text Extraction Handler
# -----------------------------------------
class ExtractionTools:
    async def text_extraction_for_scanned_and_selectable_file_for_json_format_through_gemini(self, file):
        input_token = 0
        output_token = 0
        extracted_text = ""

        filename = file["filename"]
        text_file_name = str(uuid4()) + filename.split("/")[-1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file_content = file["content"]
            temp_file.write(temp_file_content)
            temp_file_path = temp_file.name

        docs = fitz.open(temp_file_path)
        for page_num in range(len(docs)):
            data = docs[page_num].get_text("text")
            extracted_text += data

        # Check if it's not a selectable PDF (low text length)
        if len(extracted_text.strip()) < 50:
            extracted_text = ""
            with open("./extract.txt", mode='w') as text_file:
                images = convert_from_path(temp_file_path)
                for i, image in enumerate(images):
                    image = np.array(image)
                    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    text = pytesseract.image_to_string(grey)
                    extracted_text += text
                    text_file.write(f"{text_file_name} - Page No {i + 1}\n\n")
                    text_file.write(text + "\n\n")


        prompt = f'''
        You are a billing parser that generates strictly JSON-formatted responses. Follow these strict guidelines:

        Output Format:
        {{
            "invoice_no": "string",
            "date": "string",
            "stokist": {{
                "name": "string",
                "address": {{
                    "street": "string",
                    "city": "string",
                    "state": "string",
                    "zip_code": "string"
                }},
                "phone": "string",
                "GSTIN": "string",
                "DL_No": "string"
            }},
            "chemist": {{
                "name": "string",
                "address": {{
                    "street": "string",
                    "city": "string",
                    "state": "string",
                    "zip_code": "string"
                }},
                "GSTIN": "string",
                "DL_No": "string"
            }},
            "items": [
                {{
                    "product_name": "string",
                    "pack": "string",
                    "batch": "string",
                    "HSN": "string",
                    "expiry": "YYYY-MM",
                    "quantity": "string",
                    "MRP": "string",
                    "GST_percent": "string",
                    "amount": "string"
                }}
            ],
            "totals": {{
                "subtotal": 0.0,
                "discount": 0.0,
                "SGST": 0.0,
                "CGST": 0.0,
                "GST_total": 0.0,
                "grand_total": 0.0,
                "outstanding_amount": 0.0
            }}
        }}
        Basic information from the documents to be extracted:

        stokist -> the supplier who sells the medicines.
        chemist -> the buyer who purchase the medicines.
        invoice number -> unique sequential code that is systematically assigned to invoices.
        date -> date of purchasing the medicines.
        items -> list or table of all medicines details.

        Stokist Details :
        name -> Name of the stokist.
        address -> Residential address of stokist.
        street -> Street address.
        city -> City name.
        state -> State name (abbreviation or full).
        zip_code -> Postal code.
        phone -> contact number of stockist.
        GSTIN -> 15-digit PAN-based number allotted to stokist.
        DL_NO -> Drug license number alloted to stokist.

        Chemist Details :
        name -> Name of the chemist.
        address -> Residential address of chemist.
        street -> Street address.
        city -> City name.
        state -> State name (abbreviation or full).
        zip_code -> Postal code.
        GSTIN -> 15-digit PAN-based number allotted to chemist.
        DL_NO -> Drug license number alloted to chemist.

        Item Details:
        subtotal -> The total cost of all items before applying any taxes or discounts.
        discount -> Any reduction applied to the subtotal before calculating tax.
        SGST -> The tax collected by the state government.
        CGST -> The tax collected by the central government.
        GST_total -> The sum of SGST and CGST.
        grand_total -> The final amount to be paid, including taxes.
        outstanding_amount -> The remaining balance the buyer still owes to the supplier.

        
        Input Text:
        {extracted_text}
        '''

        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        content = response.text.strip()

        if content.startswith("```json"):
            content = content[len("```json"):].strip()
        if content.endswith("```"):
            content = content[:-len("```")].strip()

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Gemini response not valid JSON.")

        data["token"] = {
            "input_token": input_token,
            "output_token": output_token
        }

        return data

# -----------------------------------------
# FastAPI App and Endpoint
# -----------------------------------------
app = FastAPI()
extractor = ExtractionTools()

@app.post("/extract-bill")
async def extract_bill(file: UploadFile = File(...)):
    file_data = {
        "filename": file.filename,
        "content": await file.read()
    }
    data = await extractor.text_extraction_for_scanned_and_selectable_file_for_json_format_through_gemini(file_data)
    return JSONResponse(content=data)

# -----------------------------------------
# End of Code
# -----------------------------------------

