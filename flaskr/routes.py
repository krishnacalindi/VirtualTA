from flask import render_template, url_for, redirect, flash, session, request
from flaskr import app, mail, conn, blob_service_client, blob_container
from flaskr.forms import LoginForm, RegisterForm, DFAForm, SyllabusForm, AddForm
from flaskr.models import User
from flaskr.utils import askQuestion
from flask_mail import Message
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
import pyotp
import uuid
conversation = {}

@app.route('/')
def welcome():
    if current_user.is_authenticated:
        if current_user.ta == 1:
            return redirect(url_for('ta_land'))
        else:
            return redirect(url_for('stu_land'))
    return render_template('welcome.html', title="Welcome", rightlinks=[['login', 'Login'], ['register', 'Register']])

@app.route('/auth/login', methods=['GET', 'POST'])
def login(): 
    if current_user.is_authenticated:
        if current_user.ta == 1:
            return redirect(url_for('ta_land'))
        else:
            return redirect(url_for('stu_land'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.getUser(form.username.data, form.password.data)
        if user is None:
            flash("Incorrect username or password", 'error')
            return redirect(url_for('login'))
        else:
            session['email'] = user.email
            return redirect(url_for('sendmail'))
    return render_template('auth/login.html', title="Login", form=form, leftlinks = [['welcome', 'Home']], rightlinks=[['register', 'Register']])

@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.ta == 1:
            return redirect(url_for('ta_land'))
        else:
            return redirect(url_for('stu_land'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.createUser(form.username.data, form.email.data, generate_password_hash(form.password.data))
        if user is None:
            flash("An error occured while registering user",'error')
            return redirect(url_for('register'))
        else:
            flash("Successfully registered user", 'success')
            return redirect(url_for('login'))
    return render_template('auth/register.html', title="Register", form=form, leftlinks = [['welcome', 'Home']], rightlinks=[['login', 'Login']])

@app.route('/auth/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('welcome'))

@app.route('/auth/sendmail')
def sendmail():
    if current_user.is_authenticated:
        if current_user.ta == 1:
            return redirect(url_for('ta_land'))
        else:
            return redirect(url_for('stu_land'))
    try:
        email = session['email']
        mail_message = Message('One Time Password', sender=app.config['MAIL_USERNAME'], recipients=[email])
        secret_key = pyotp.random_base32()
        totp = pyotp.TOTP(secret_key, interval=300, digits=6)
        otp = totp.now()
        session['secret_key'] = secret_key
        mail_message.html = render_template('mail/otp.html', otp=otp)
        mail.send(mail_message)
        return redirect(url_for('dfa')) 
    except:
        session.clear()
        flash('An error occured', 'error')
        return redirect(url_for('welcome'))

@app.route('/auth/dfa', methods=['GET', 'POST'])
def dfa():
    if current_user.is_authenticated:
        if current_user.ta == 1:
            return redirect(url_for('ta_land'))
        else:
            return redirect(url_for('stu_land'))
    try:
        email = session['email']
        form = DFAForm()
        if form.validate_on_submit():
            totp = pyotp.TOTP(session['secret_key'], interval=300)
            if totp.verify(form.otp.data):
                user = User.getUserFromEmail(email)
                if user is not None:
                    session.clear()
                    login_user(user)
                    if current_user.ta == 1:
                        return redirect(url_for('ta_land'))
                    else:
                        return redirect(url_for('stu_land'))    
                else:
                    raise MemoryError("Retrieval error",'error')
            else:
                session.clear()
                flash('Incorrect one time password','error')
                return redirect(url_for('login'))
        return render_template('auth/dfa.html', title="Dual Factor Authentication", form=form)
    except:
        session.clear()
        flash('An error occured','error')
        return redirect(url_for('welcome'))

@app.route('/stu/land')
@login_required
def stu_land():
    cursor = conn.cursor()
    get_courses_command = "SELECT * FROM course_population WHERE user_id = ?;"
    cursor.execute(get_courses_command, (current_user.id,))
    courselist = cursor.fetchall()
    courses = []
    for row in courselist:
        conversation[row[0]] = []
        get_course_info = "SELECT * from courses where course_id = ?;"
        cursor.execute(get_course_info, (row[0],))
        course_info = cursor.fetchone()
        courses.append([course_info[0], (str(course_info[1]) + " " + str(course_info[2]) + " " + str(course_info[3]))])
    if current_user.ta == 1:
        return render_template('/stu/land.html', title= current_user.username + " - Home", leftlinks = [['stu_land', 'Home'], ['ta_land', 'TA View']], rightlinks=[['logout', 'Logout']], courses=courses)
    return render_template('/stu/land.html', title= current_user.username + " - Home", leftlinks = [['stu_land', 'Home']], rightlinks=[['logout', 'Logout']], courses=courses)

@app.route('/stu/<course_id>/chatbot', methods=['GET', 'POST'])
def stu_chatbot(course_id):
    if course_id not in conversation:
                conversation[course_id] = []
    if request.method == 'POST':
        if not request.form['question']:
            return render_template('stu/chatbot.html', title = current_user.username+" - Chatbot", conversation=conversation[course_id], leftlinks = [['stu_land', 'Home']], rightlinks=[['logout', 'Logout']])
        else:
            cursor = conn.cursor()
            syllabus_name_command = 'SELECT file_name FROM syllabus WHERE course_id = ?;'
            cursor.execute(syllabus_name_command, (course_id,))
            question = request.form['question']
            file_name = cursor.fetchone()
            if file_name is None:
                conversation_answer = "Chatbot: No syllabus uploaded."
            else:
                answer = askQuestion(question, file_name[0])
                conversation_answer = "Chatbot: " + answer
            conversation_question = str(current_user.username) + ": "  + question
            conversation[course_id].insert(0, [conversation_answer, conversation_question])
            return render_template('stu/chatbot.html', title = current_user.username+" - Chatbot", conversation=conversation[course_id], leftlinks = [['stu_land', 'Home']], rightlinks=[['logout', 'Logout']])
    else:
        return render_template('stu/chatbot.html', title = current_user.username+" - Chatbot", conversation=conversation[course_id], leftlinks = [['stu_land', 'Home']], rightlinks=[['logout', 'Logout']])

@app.route('/ta/land')
@login_required
def ta_land():
    if current_user.ta != 1:
        return redirect(url_for('stu_land'))
    cursor = conn.cursor()
    get_courses_command = "SELECT * FROM course_population WHERE user_id = ?;"
    cursor.execute(get_courses_command, (current_user.id,))
    courselist = cursor.fetchall()
    courses = []
    for row in courselist:
        conversation[row[0]] = []
        get_course_info = "SELECT * from courses where course_id = ?;"
        cursor.execute(get_course_info, (row[0],))
        course_info = cursor.fetchone()
        courses.append([course_info[0], (str(course_info[1]) + " " + str(course_info[2]) + " " + str(course_info[3]))])
    return render_template('/ta/land.html', title= current_user.username + " - Home", leftlinks = [['ta_land', 'Home'], ['stu_land', 'Student View']], rightlinks=[['logout', 'Logout']], courses=courses)

@app.route('/ta/<course_id>')
@login_required
def ta_course(course_id):
    if current_user.ta != 1:
        return redirect(url_for('stu_land'))
    return render_template('ta/course.html', title= current_user.username + " - Course Homepage", leftlinks = [['ta_land', 'Home']], rightlinks=[['logout', 'Logout']], course_id=course_id, syllabus_link=url_for('ta_syl', course_id=course_id), add_link=url_for('ta_add', course_id=course_id))

@app.route('/ta/<course_id>/syl', methods=['GET', 'POST'])
@login_required
def ta_syl(course_id):
    if current_user.ta != 1:
        return redirect(url_for('stu_land'))
    form = SyllabusForm()
    if form.validate_on_submit():
        blob_name = str(uuid.uuid4()) + ".pdf"
        blob_client = blob_service_client.get_blob_client(container=blob_container, blob=blob_name)
        try:
            with form.syllabus.data.stream as file_stream:
                blob_client.upload_blob(file_stream, overwrite=True)
            flash("Syllabus uploaded successfully",'success')
            syllabus_info_command = f"INSERT INTO syllabus (file_name, container_name, course_id) VALUES (?, ?, ?);"
            cursor = conn.cursor()
            cursor.execute(syllabus_info_command, (blob_name, blob_container, course_id))
            cursor.commit()
        except Exception as e:
            print(str(e))
            flash("Error in uploading syllabus",'error')
        return redirect(url_for('ta_land'))
    return render_template('ta/syl.html', title= current_user.username + " - Syllabus", leftlinks = [['ta_land', 'Home']], form=form, rightlinks=[['logout', 'Logout']])

@app.route('/ta/<course_id>/add', methods=['GET', 'POST'])
@login_required
def ta_add(course_id):
    if current_user.ta != 1:
        return redirect(url_for('stu_land'))
    form = AddForm()
    if form.validate_on_submit():
        username = form.username.data
        get_student_command = "SELECT id from user_info where username = ?;"
        cursor = conn.cursor()
        cursor.execute(get_student_command, (username,))
        id = cursor.fetchone()[0]
        if id is None:
            flash("Student username does not exist",'error')
            redirect(url_for('ta_course', course_id=course_id))
        else:
            add_student_command = "INSERT INTO course_population (course_id, user_id) VALUES (?, ?);"
            try:
                cursor.execute(add_student_command, (course_id, id))
                cursor.commit()
                flash("Student added successfully",'success')
                redirect(url_for('ta_course', course_id=course_id))
            except:
                flash("Error occured while adding student",'error')
                redirect(url_for('ta_course', course_id=course_id))
    return render_template('ta/add.html', title= current_user.username + " - Add Student", leftlinks = [['ta_land', 'Home']], form=form, rightlinks=[['logout', 'Logout']])

@app.errorhandler(Exception)
def error_handling(error):
    logout()
    session.clear()
    flash("An unexpected error occured",'error')
    return redirect(url_for('welcome'))