from openai import OpenAI
import fitz
from azure.storage.blob import BlobServiceClient
from io import BytesIO
from flaskr import blob_service_client

# Function to interact with OpenAI API
def virtual_ta_question(question, syllabus_text):
    OPENAI_API_KEY = "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"
    client = OpenAI(api_key=OPENAI_API_KEY)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a teaching assistant for university level courses at the University of Texas at Dallas. Provide concise responses unless otherwise instructed by the student. Cite your responses from the syllabus in the format Section, Page Number. Do not answer questions outside the scope of the syllabus content."},
            {"role": "system", "content": syllabus_text},  # Adding syllabus text as context
            {"role": "user", "content": question},
        ]
    )
    return completion.choices[0].message.content

def get_syllabus_text(syllabusName):
    blob_client = blob_service_client.get_blob_client(container='syllabi', blob=syllabusName)
    blob_data = BytesIO(blob_client.download_blob().readall())

    pdf_document = fitz.open("pdf", blob_data)
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    pdf_document.close()
    return text

def askQuestion(question, syllabusName):
    syllabus_text = get_syllabus_text(syllabusName)
    return virtual_ta_question(question, syllabus_text)
