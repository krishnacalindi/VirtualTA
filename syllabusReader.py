import pyodbc
import PyPDF2
import json

# Connection string details
server = 'group72.database.windows.net'
database = 'Group72'
username = 'MeepLeader'
password = '5_of_us_in_group_72'
driver = '{ODBC Driver 18 for SQL Server}'

# Connect to the database
conn_str = (
    f"Driver={driver};"
    f"Server={server};"
    f"Database={database};"
    f"Uid={username};"
    f"Pwd={password};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

def create_database():
    """Create syllabi table if it doesn't exist."""
    cursor.execute('''IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'syllabi')
                      CREATE TABLE syllabi (
                          id INT PRIMARY KEY IDENTITY(1,1),
                          file_name NVARCHAR(255),
                          section NVARCHAR(255),
                          course_description NVARCHAR(MAX),
                          homework NVARCHAR(MAX),
                          exam NVARCHAR(MAX),
                          class_time NVARCHAR(MAX),
                          office_hours NVARCHAR(MAX),
                          grade_distribution NVARCHAR(MAX),
                          attendance NVARCHAR(MAX),
                          textbook NVARCHAR(MAX),
                          instructor NVARCHAR(MAX),
                          TA NVARCHAR(MAX),
                          miscellaneous NVARCHAR(MAX)
                      )''')

def insert_syllabus_info(file_name, syllabus_info):
    """Insert syllabus information into the database."""
    for section, info in syllabus_info.items():
        cursor.execute("INSERT INTO syllabi (file_name, section, course_description, homework, exam, class_time, office_hours, grade_distribution, attendance, textbook, instructor, TA, miscellaneous) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (file_name, section, info.get('content', ''), info.get('homework', ''), info.get('exam', ''), info.get('class_time', ''), info.get('office_hours', ''), info.get('grade_distribution', ''), info.get('attendance', ''), info.get('textbook', ''), info.get('instructor', ''), info.get('TA', ''), info.get('miscellaneous', '')))
    conn.commit()


def insert_data(table_name, section, content):
    """Insert data into the specified table."""
    cursor.execute(f"INSERT INTO {table_name} (section, content) VALUES (?, ?)", (section, content))
    conn.commit()

import re

def parse_syllabus(file_contents):
    """Parse syllabus contents."""
    syllabus_info = {}
    
    # Define regular expression pattern to match section titles
    section_pattern = re.compile(r"Section \d+", re.IGNORECASE)
    
    # Split the syllabus content into sections based on the section pattern
    sections = section_pattern.split(file_contents)[1:]
    
    for i, section_text in enumerate(sections):
        # Extract section title
        section_title = "Section " + str(i + 1)
        
        # Extract content (excluding section title)
        content_start_index = file_contents.find(section_text)
        content_end_index = content_start_index + len(section_text)
        content = file_contents[content_end_index:]
        
        # Store section title and content
        syllabus_info[section_title] = {
            "content": section_text.strip(),
            "homework": "",  # Update with actual extraction logic
            "exam": "",      # Update with actual extraction logic
            # Add other fields as needed
        }
    
    return syllabus_info


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    return text

if __name__ == "__main__":
    create_database()
    pdf_path = '/Users/juanctavira/Desktop/AIsyllabus.pdf'
    pdf_text = extract_text_from_pdf(pdf_path)
    syllabus_info = parse_syllabus(pdf_text)

    # Print out the parsed syllabus information
    for section, info in syllabus_info.items():
        print(f"Section: {section}")
        print(f"Content: {info['content']}")
        print(f"Homework: {info['homework']}")
        print(f"Exam: {info['exam']}")

    # Insert parsed syllabus information into the database
    for section, info in syllabus_info.items():
        insert_data("syllabi", section, info["content"])
     
    print("Syllabus information saved to the database.")

# Close the cursor and the connection
cursor.close()
conn.close()
