from flask import render_template, url_for, redirect, flash, session, request
from flaskr import app, mail, conn, blob_service_client, blob_container
from flaskr.forms import LoginForm, RegisterForm, DFAForm, SyllabusForm
from flaskr.models import User
from flaskr.utils import askQuestion
from flask_mail import Message
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
import pyotp
import uuid
conversation = []

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
            flash('Incorrect username or password.')
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
            flash("An error occured while registering user.")
            return redirect(url_for('register'))
        else:
            flash("Successfully registered user.")
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
        flash('An error occured.')
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
                    raise MemoryError("Retrieval error.")
            else:
                session.clear()
                flash('Incorrect one time password.')
                return redirect(url_for('login'))
        return render_template('auth/dfa.html', title="Dual Factor Authentication", form=form)
    except:
        session.clear()
        flash('An error occured.')
        return redirect(url_for('welcome'))

@app.route('/stu/land')
@login_required
def stu_land():
    cursor = conn.cursor()
    get_courses_command = "SELECT * FROM courses WHERE user_id = ?;"
    cursor.execute(get_courses_command, current_user.id)
    courses = []
    for row in cursor:
        courses.append([row[0], (str(row[1]) + " " + str(row[2]) + " " + str(row[3]))])
    return render_template('/stu/land.html', title= current_user.username + " - Home", leftlinks = [['stu_land', 'Home']], rightlinks=[['logout', 'Logout']], courses=courses)

@app.route('/stu/<course_id>/chatbot', methods=['GET', 'POST'])
def stu_chatbot(course_id):
    if request.method == 'POST':
        if not request.form['question']:
            return render_template('stu/chatbot.html', title = current_user.username+" - Chatbot", conversation=conversation, leftlinks = [['stu_land', 'Home']], rightlinks=[['logout', 'Logout']])
        else:
            question = request.form['question']
            conversation.insert(0, question)
            answer = askQuestion(question, "")
            conversation.insert(0, answer)
            # send question to that thing and get answer back pls add to convo and render template.
            return render_template('stu/chatbot.html', title = current_user.username+" - Chatbot", conversation=conversation, leftlinks = [['stu_land', 'Home']], rightlinks=[['logout', 'Logout']])
    else:
        return render_template('stu/chatbot.html', title = current_user.username+" - Chatbot", conversation=conversation, leftlinks = [['stu_land', 'Home']], rightlinks=[['logout', 'Logout']])

@app.route('/ta/land')
@login_required
def ta_land():
    if current_user.ta != 1:
        return redirect(url_for('stu_land'))
    cursor = conn.cursor()
    get_courses_command = "SELECT * FROM courses WHERE user_id = ?;"
    cursor.execute(get_courses_command, current_user.id)
    courses = []
    for row in cursor:
        courses.append([row[0], (str(row[1]) + " " + str(row[2]) + " " + str(row[3]))])
    return render_template('/ta/land.html', title= current_user.username + " - Home", leftlinks = [['ta_land', 'Home']], rightlinks=[['logout', 'Logout']], courses=courses)

@app.route('/ta/<course_id>')
@login_required
def ta_course(course_id):
    if current_user.ta != 1:
        return redirect(url_for('stu_land'))
    return render_template('ta/course.html', title= current_user.username + " - Course Homepage", leftlinks = [['ta_land', 'Home']], rightlinks=[[f"'ta_syl', course_id={course_id}", 'Syllabus'], ['logout', 'Logout']], course_id=course_id)

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
            flash("Syllabus uploaded successfully.")
            syllabus_info_command = f"INSERT INTO syllabus (file_name, container_name, course_id) VALUES (?, ?, ?);"
            cursor = conn.cursor()
            cursor.execute(syllabus_info_command, (blob_name, blob_container, course_id))
            cursor.commit()
        except Exception as e:
            print(str(e))
            flash("Error in uploading syllabus.")
        return redirect(url_for('ta_land'))
    return render_template('ta/syl.html', title= current_user.username + " - Syllabus", leftlinks = [['ta_land', 'Home']], form=form, rightlinks=[['logout', 'Logout']])

@app.route('/ta/rules/view')
@login_required
def ta_rules_view():
    if current_user.ta != 1:
        return redirect(url_for('stu_land'))
    return "rules"

@app.route('/ta/rules/update')
@login_required
def ta_rules_update():
    if current_user.ta != 1:
        return redirect(url_for('stu_land'))
    return "update"