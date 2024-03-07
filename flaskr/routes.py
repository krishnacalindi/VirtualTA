from flask import render_template, url_for, redirect
from flaskr import app, mail
from flaskr.forms import LoginForm, RegisterForm, DFAForm, SyllabusForm
from flask_mail import Message

@app.route('/')
def welcome():
    return render_template('welcome.html', title="Welcome", links=[['login', 'Login'], ['register', 'Register']])

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect(url_for('sendmail'))
    return render_template('auth/login.html', title="Login", form=form, links=[['welcome', 'Home'], ['register', 'Register']])

@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        return "got form"
    return render_template('auth/register.html', title="Register", form=form, links=[['welcome', 'Home'], ['login', 'Login']])

@app.route('/auth/logout')
def logout():
    return redirect(url_for('welcome'))

@app.route('/auth/sendmail')
def sendmail():
    mail_message = Message('Test', sender=app.config['MAIL_USERNAME'], recipients=[''])
    mail_message.body = 'Testing to see whether this works!!!'
    mail.send(mail_message)
    return redirect(url_for('dfa')) 

@app.route('/auth/dfa', methods=['GET', 'POST'])
def dfa():
    form = DFAForm()
    if form.validate_on_submit():
        return "got dfa"
    return render_template('auth/dfa.html', title="Dual Factor Authentication", form=form)

@app.route('/stu/land')
def stu_land():
    return render_template('/stu/land.html', title="Student - Home" ,links=[['logout', 'Logout']])

@app.route('/ta/land')
def ta_land():
    return render_template('/stu/land.html', title="TA - Home" ,links=[['logout', 'Logout'], ['ta_syl', 'Syllabus']])

@app.route('/ta/syl', methods=['GET', 'POST'])
def ta_syl():
    form = SyllabusForm()
    if form.validate_on_submit():
        return "got the syllabus!"
    return render_template('ta/syl.html', title="TA - Syllabus", form=form, links=[['logout', 'Logout']])