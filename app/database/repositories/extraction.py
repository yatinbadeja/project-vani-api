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
            "date": "string",
            "stokist": {{
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
        subtotal -> The total price of all items before adding any type taxes or discounts.
        discount -> Any type of deduction applied to the subtotal before calculating tax.
        SGST -> The total tax amount collected by the state government.
        CGST -> The total tax amount collected by the central government.
        GST_total -> The sum of SGST and CGST.
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


#Orders Collection

db.Orders.insertOne({
    _id: "order_uuid", // Generate a new UUID
    stockist_id: "stockist_uuid", //  ID of the stockist (seller)
    chemist_id: "chemist_uuid", // ID of the chemist (buyer)
    order_date: new Date("YYYY-MM-DD"), // From bill
    status: "Pending", // Initial status
    total_amount: total_amount_from_bill, // From bill
    created_at: new Date(),
    updated_at: new Date()
});
const the_order_id = "order_uuid"; // Capture generated order_id

#SaleDetails Collection

const saleDetails = [
    {
        product_id: "product_uuid_1", // From your product catalog
        quantity: 2, // From bill
        unit_price: 25.00, // From bill
        sale_id: the_order_id, //  _id of the order
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        product_id: "product_uuid_2",
        quantity: 1,
        unit_price: 50.00,
        sale_id: the_order_id,
        created_at: new Date(),
        updated_at: new Date()
    },
    // Add more items as needed from the bill
];
db.SaleDetails.insertMany(saleDetails);

#ProductStock Collection

saleDetails.forEach(item => {
    db.ProductStock.updateOne(
        { product_id: item.product_id }, //  Match by product_id
        { $inc: { stock_available: -item.quantity } } // Reduce stock
    );
})
