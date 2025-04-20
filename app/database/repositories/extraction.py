import json
import cv2
import fitz 
import numpy as np
import pytesseract
import tempfile
from uuid import uuid4
from pdf2image import convert_from_path
from app.Config import ENV_PROJECT
# import google
# # from google import genai
# from app.utils.openai import gemini
# from google import genai
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

import google.generativeai as genai

genai.configure(api_key=ENV_PROJECT.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

class ExtractionTools:
    async def text_extraction_for_scanned_and_selectable_file_for_json_format_through_gemini(self, file):
        input_token = 0
        output_token = 0
        extracted_text = ""

        filename = file.filename
        text_file_name = str(uuid4()) + filename.split("/")[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file_content = await file.read()
            temp_file.write(temp_file_content)
            temp_file_path = temp_file.name
        
        docs = fitz.open(temp_file_path)
        for page_num in range(len(docs)):
            data = docs[page_num].get_text("text")
            extracted_text += data
        # print(extracted_text)

        if len(extracted_text) < 50:
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
                    text_file.write("\n\n")
        # print(extracted_text)
        prompt = f'''
        You are a billing parser that extract the following information from the chemist shop bill text into a JSON object. If a field is not found, use "null". Follow these strict guidelines:

          Output Format:
        {{
            "invoice_no": "string",
            "date": "DD-MM-YYYY",
            "stockist": {{
                "name": "string",
                "address": {{
                    "street_address_1": "string",
                    "street_address_2": "string",
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
                    "street_address_1": "string",
                    "street_address_2": "string",
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
                    "rate": "string",
                    "GST_percent": "string",
                    "amount": "string"
                }}
            ],
            "totals": {{
                "subtotal": 0.0,
                "discount": 0.0,
                "GST_total": 0.0,
                "grand_total": 0.0,
                "outstanding_amount": 0.0
            }}
        }}
        Basic information from the documents to be extracted:

        stokist -> the supplier who sells the medicines.
        chemist -> the buyer who purchase the medicines.
        invoice_no -> unique sequential code that is systematically assigned to invoices.
        date -> Date of the invoice in DD-MM-YYYY format.
        items -> list or table of all medicines details.

        Stokist Details :
        name -> Name of the stokist.
        address -> Residential address of stokist.
        street_address_1 -> First part of Street address.
        street_address_2 -> Second part of Street address.
        city -> City name.
        state -> State name (abbreviation or full).
        zip_code -> Postal code.
        phone -> contact number of stockist.
        GSTIN -> 15-digit PAN-based number allotted to stokist.
        DL_NO -> Drug license number alloted to stokist.

        Chemist Details :
        name -> Name of the chemist.
        address -> Residential address of chemist.
        street_address_1 -> First part of Street address.
        street_address_2 -> Second part of Street address.
        city -> City name.
        state -> State name (abbreviation or full).
        zip_code -> Postal code.
        GSTIN -> 15-digit PAN-based number allotted to chemist.
        DL_NO -> Drug license number alloted to chemist.

        Item Details:
        product_name -> Name of the product.
        pack -> Pack size of the product(Ltr, ml, Kg, No. of Tablets per pack).
        batch -> Batch number of the product.
        HSN -> Harmonized System of Nomenclature code of the product.
        expiry -> Expiry date of the product in YYYY-MM format.
        quantity -> Number of units of the product.
        MRP -> Maximum Retail Price of the product.
        rate -> Rate of the product.
        GST_percent -> Goods and Services Tax percentage(Sum of all type of GST(SGST + CGST + IGST)) applicable to the product.
        amount -> Total amount for the product (quantity * rate).
        
        Totals Details:
        subtotal -> The total amount of all the items excluding the taxes and discounts.
        discount -> Any type of deduction applied to the subtotal before calculating tax.
        GST_total -> The sum of all type of GST(SGST, IGST and CGST).
        grand_total -> The final/net amount of the invoice after deducting the discount and adding the total tax amount that is to be paid, including taxes.
        outstanding_amount -> The remaining balance the buyer still owes to the supplier.


        Input Text:
        {extracted_text}
        '''
        response = model.generate_content(prompt)
        content = response.text.strip()
        # print(content)
        if content.startswith("```json"):
            content = content[len("```json"):].strip()
        if content.endswith("```"):
            content = content[:-len("```")].strip()

        data = json.loads(content)
        # print(data)
        # data["token"] = {
        #     "input_token": input_token,  # Placeholder: replace with actual counting logic if need
        # }
        return data

extraction_tools = ExtractionTools()




#SaleDetails Collection

from pymongo import MongoClient
from datetime import datetime

# 1.  Establish a connection to MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB connection string
db = client['your_database_name']  # Replace with your actual database name

# 2.  Data to be inserted
the_order_id = "order_uuid"  #  Replace with your actual order ID (UUID)

sale_details = [
    {
        "product_id": "product_uuid_1",  # Replace with actual product UUID
        "quantity": 2,
        "unit_price": 25.00,
        "sale_id": the_order_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "product_id": "product_uuid_2",  # Replace with actual product UUID
        "quantity": 1,
        "unit_price": 50.00,
        "sale_id": the_order_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    #  Add more items as needed
]

# 3. Insert into SaleDetails Collection
sale_details_collection = db['SaleDetails']  # Get the SaleDetails collection
sale_details_collection.insert_many(sale_details)  # Use insert_many


# 4. Update ProductStock Collection
product_stock_collection = db['ProductStock'] #Get the ProductStock Collection
for item in sale_details:
    product_id = item['product_id']
    quantity = item['quantity']
    
    product_stock_collection.update_one(
        {'product_id': product_id},  # Filter: match by product_id
        {'$inc': {'stock_available': quantity}}  # Update: decrement stock
    )

# 5. Close the connection (optional, but good practice)
client.close()
