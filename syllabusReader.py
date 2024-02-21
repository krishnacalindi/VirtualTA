import sqlite3
import PyPDF2
import json

DATABASE = 'syllabus.db'

def create_database():
    """Create SQLite database and syllabi table if they don't exist."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS syllabi
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 file_name TEXT,
                 section TEXT,
                 content TEXT)''')
    conn.commit()
    conn.close()

def insert_syllabus_info(file_name, syllabus_info):
    """Insert syllabus information into the database."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''INSERT INTO syllabi (file_name, content)
                 VALUES (?, ?)''', (file_name, json.dumps(syllabus_info)))
    conn.commit()
    conn.close()

def parse_syllabus(file_contents):
    """Parse syllabus contents."""
    syllabus_info = {}
    
    # Split the syllabus content into sections
    sections = file_contents.split("Course Syllabus   Page ")[1:]
    
def parse_syllabus(file_contents):
    """Parse syllabus contents."""
    syllabus_info = {}
    
    # Split the syllabus content into sections
    sections = file_contents.split("Course Syllabus   Page ")[1:]
    
    for i, section_text in enumerate(sections):
        # Extract section title
        section_title = "Section " + str(i + 1)
        
        # Extract content
        content_start_index = section_text.find("Course Description")
        content_end_index = section_text.find("Student Learning Objectives/Outcomes")
        content = section_text[content_start_index:content_end_index]

        # Extract and store homework assignments
        homework_start_index = content.find("Homework")
        homework_end_index = content.find("Projects")
        homework_content = content[homework_start_index:homework_end_index]
        
        # Extract and store exam info
        exam_start_index = content.find("Midterm")
        exam_end_index = content.find("Exam/Final")
        exam_content = content[exam_start_index:exam_end_index]
        
        # Extract and store class meeting time and location
        class_time_index = content.find("Class meeting time and location")
        class_time_end_index = content.find("Office Hours")
        class_time_content = content[class_time_index:class_time_end_index]

        # Extract and store office hours
        office_hours_index = content.find("Office Hours")
        office_hours_end_index = content.find("Grade Distribution")
        office_hours_content = content[office_hours_index:office_hours_end_index]

        # Extract and store grade distribution
        grade_dist_index = content.find("Grade Distribution")
        grade_dist_end_index = content.find("Attendance")
        grade_dist_content = content[grade_dist_index:grade_dist_end_index]

        # Extract and store attendance policy
        attendance_index = content.find("Attendance")
        attendance_end_index = content.find("End of Syllabus")
        attendance_content = content[attendance_index:attendance_end_index]

        # Store section title and content
        syllabus_info[section_title] = {
            "content": content.strip(),
            "homework": homework_content.strip(),
            "exam": exam_content.strip(),
            "class_time": class_time_content.strip(),
            "office_hours": office_hours_content.strip(),
            "grade_distribution": grade_dist_content.strip(),
            "attendance": attendance_content.strip()
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
    insert_syllabus_info(pdf_path, syllabus_info)
    print("Syllabus information saved to the database.")
