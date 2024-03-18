from flask import render_template, url_for, redirect, flash, session
from flaskr import app, mail, conn
from flaskr.forms import LoginForm, RegisterForm, DFAForm, SyllabusForm
from flask_mail import Message
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash
from flaskr.models import User
import random

@app.route('/')
def welcome():
    return render_template('welcome.html', title="Welcome", links=[['login', 'Login'], ['register', 'Register']])

@app.route('/auth/login', methods=['GET', 'POST'])
def login(): 
    form = LoginForm()
    if form.validate_on_submit():
        user = User.getUser(form.username.data, form.password.data)
        if user is None:
                flash('Incorrect username or password.')
                return redirect(url_for('login'))
        else:
                login_user(user)
                session['email'] = user.email
                return redirect(url_for('sendmail'))
    return render_template('auth/login.html', title="Login", form=form, links=[['welcome', 'Home'], ['register', 'Register']])

@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.createUser(form.username.data, form.email.data, generate_password_hash(form.password.data))
        if user is None:
             flash("An error occured while registering user.")
        else:
             flash("Successfully registered user.")
        return render_template('auth/login.html', title="Login", form=form, links=[['welcome', 'Home'], ['register', 'Register']])
    return render_template('auth/register.html', title="Register", form=form, links=[['welcome', 'Home'], ['login', 'Login']])

@app.route('/auth/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('welcome'))

@app.route('/auth/sendmail')
@login_required
def sendmail():
    mail_message = Message('Test', sender=app.config['MAIL_USERNAME'], recipients=[session['email']])
    numbers = "0123456789"
    otp = ""
    for i in range(4) :
        otp += numbers[random.randint(0, 9)]
    session[otp] = otp
    mail_message.body = 'OTP = ' + otp
    mail.send(mail_message)
    return redirect(url_for('dfa')) 

@app.route('/auth/dfa', methods=['GET', 'POST'])
@login_required
def dfa():
    form = DFAForm()
    if form.validate_on_submit():
        if session[dfa] == form.otp.data:
            return redirect(url_for('stu_land'))
        else:
             flash('Incorrect one time password.')
    return render_template('auth/dfa.html', title="Dual Factor Authentication", form=form)

@app.route('/stu/land')
@login_required
def stu_land():
    return render_template('/stu/land.html', title="Student - Home" ,links=[['logout', 'Logout']])

@app.route('/ta/land')
@login_required
def ta_land():
    return render_template('/stu/land.html', title="TA - Home" ,links=[['logout', 'Logout'], ['ta_syl', 'Syllabus']])

@app.route('/ta/syl', methods=['GET', 'POST'])
@login_required
def ta_syl():
    form = SyllabusForm()
    if form.validate_on_submit():
        return "got the syllabus!"
    return render_template('ta/syl.html', title="TA - Syllabus", form=form, links=[['logout', 'Logout']])