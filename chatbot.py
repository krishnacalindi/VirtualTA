# requirements:
# pip install openai
# pip install PyMuPDF

# instead of pdf text connect chatbot to database with - slides, question&answer bank, syllabus information

from openai import OpenAI
import fitz  # Import the PyMuPDF library

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ''
    with fitz.open(pdf_path) as document:
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            text += page.get_text()
    return text

# Function to interact with OpenAI API
def virtual_ta_question(question, syllabus_text):
    OPENAI_API_KEY = "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"
    client = OpenAI(api_key=OPENAI_API_KEY)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a teaching assistant for university level courses at the University of Texas at Dallas. Provide concise responses unless otherwise instructed by the student. Cite your responses, page number / line number from syllabus."},
            {"role": "system", "content": syllabus_text},  # Adding syllabus text as context
            {"role": "user", "content": question},
        ]
    )

    return completion.choices[0].message.content

# Main function to interact with user
def main():
    # Path to the syllabus PDF file
    syllabus_pdf_path = r'C:\Users\Owner\Desktop\TAopenAI\Syllabus.pdf'

    # Extract text from syllabus PDF
    syllabus_text = extract_text_from_pdf(syllabus_pdf_path)

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Virtual TA: Goodbye!")
            break
        response = virtual_ta_question(user_input, syllabus_text)
        print("Virtual TA:", response)

if __name__ == "__main__":
    main()

