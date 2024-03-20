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

def parse_syllabus(file_contents):
    """Parse syllabus contents."""
    syllabus_info = {}
    
    # Define the keywords we're interested in
    keywords = [
        'course and section',
        'course_description',
        'homework',
        'exams',
        'class_time',
        'office_hours',
        'grade_distribution',
        'attendance',
        'textbook',
        'instructor',
        'TA',
        'miscellaneous'
    ]
    
    # Split the syllabus content into sections
    sections = file_contents.split("Course Syllabus   Page ")[1:]
    
    # Initialize content dictionary for the section
    section_content = {}
    
    # Iterate through keywords and extract corresponding content
    for j in range(len(keywords)):
        keyword_start_index = file_contents.find(keywords[j])
        if keyword_start_index != -1:
            # Find the end index for the current keyword
            next_keyword_index = file_contents.find(keywords[j + 1]) if j + 1 < len(keywords) else file_contents.find("End of Syllabus")
            keyword_end_index = next_keyword_index if next_keyword_index != -1 else len(file_contents)
            
            # Extract content based on the current keyword
            content = file_contents[keyword_start_index+len(keywords[j]):keyword_end_index].strip()
            
            # Store content in the section dictionary
            section_content[keywords[j]] = content
    
    # Ensure all keywords are added to the dictionary even if their content is empty
    for keyword in keywords:
        section_content.setdefault(keyword, '')
    
    # Store content in the syllabus dictionary
    syllabus_info['Course'] = section_content
    
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
    
    # Print course description
    if 'course_description' in info:
        print(f"Content: {info['course_description']}")
    else:
        print("No course description available")
    
    # Print homework information
    if 'homework' in info:
        print(f"Homework: {info['homework']}")
    else:
        print("No homework information available")
    
    # Print exam information
    if 'exams' in info:
        print(f"Exam: {info['exams']}")
    else:
        print("No exam information available")
    
    # Print class time
    if 'class_time' in info:
        print(f"Class Time: {info['class_time']}")
    else:
        print("No class time information available")
    
    # Print office hours
    if 'office_hours' in info:
        print(f"Office Hours: {info['office_hours']}")
    else:
        print("No office hours information available")
    
    # Print grade distribution
    if 'grade_distribution' in info:
        print(f"Grade Distribution: {info['grade_distribution']}")
    else:
        print("No grade distribution information available")
    
    # Print attendance
    if 'attendance' in info:
        print(f"Attendance: {info['attendance']}")
    else:
        print("No attendance information available")
    
    # Print textbook
    if 'textbook' in info:
        print(f"Textbook: {info['textbook']}")
    else:
        print("No textbook information available")
    
    # Print instructor
    if 'instructor' in info:
        print(f"Instructor: {info['instructor']}")
    else:
        print("No instructor information available")
    
    # Print TA
    if 'TA' in info:
        print(f"TA: {info['TA']}")
    else:
        print("No TA information available")
    
    # Print miscellaneous
    if 'miscellaneous' in info:
        print(f"Miscellaneous: {info['miscellaneous']}")
    else:
        print("No miscellaneous information available")


     
    print("Syllabus information saved to the database.")

# Close the cursor and the connection
cursor.close()
conn.close()
