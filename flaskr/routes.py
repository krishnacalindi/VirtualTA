from flask import render_template, url_for, redirect, flash, session
from flaskr import app, mail, conn
from flaskr.forms import LoginForm, RegisterForm, DFAForm, SyllabusForm
from flask_mail import Message
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from flaskr.models import User
import random

@app.route('/')
def welcome():
    if current_user.is_authenticated:
        if session['ta'] == 1:
            return redirect(url_for('ta_land'))
        else:
            return redirect(url_for('stu_land'))
    return render_template('welcome.html', title="Welcome", rightlinks=[['login', 'Login'], ['register', 'Register']])

@app.route('/auth/login', methods=['GET', 'POST'])
def login(): 
    if current_user.is_authenticated:
        if session['ta'] == 1:
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
            session['ta'] = user.ta
            return redirect(url_for('sendmail'))
    return render_template('auth/login.html', title="Login", form=form, leftlinks = [['welcome', 'Home']], rightlinks=[['register', 'Register']])

@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if session['ta'] == 1:
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
    session.clear()
    logout_user()
    return redirect(url_for('welcome'))

@app.route('/auth/sendmail')
def sendmail():
    if current_user.is_authenticated:
        if session['ta'] == 1:
            return redirect(url_for('ta_land'))
        else:
            return redirect(url_for('stu_land'))
    try:
        email = session['email']
        mail_message = Message('One Time Password', sender=app.config['MAIL_USERNAME'], recipients=[email])
        numbers = "0123456789"
        otp = ""
        for i in range(4) :
            otp += numbers[random.randint(0, 9)]
        session['otp'] = otp
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
        if session['ta'] == 1:
            return redirect(url_for('ta_land'))
        else:
            return redirect(url_for('stu_land'))
    try:
        email = session['email']
        form = DFAForm()
        if form.validate_on_submit():
            if session['otp'] == form.otp.data:
                user = User(-2, '', email, '', session['ta'])
                user = User.getUserFromEmail(email)
                if user is not None:
                    login_user(user)
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
    return render_template('/stu/land.html', title="Student - Home", leftlinks = [['stu_land', 'Home']], rightlinks=[['logout', 'Logout']])

@app.route('/ta/land')
@login_required
def ta_land():
    return render_template('/stu/land.html', title="TA - Home", leftlinks = [['ta_land', 'Home']], rightlinks=[['logout', 'Logout'], ['ta_syl', 'Syllabus']])

@app.route('/ta/syl', methods=['GET', 'POST'])
@login_required
def ta_syl():
    form = SyllabusForm()
    if form.validate_on_submit():
        return "got the syllabus!"
    return render_template('ta/syl.html', title="TA - Syllabus", leftlinks = [['ta_land', 'Home']], form=form, rightlinks=[['logout', 'Logout']])

@app.route('/ta/rules/view')
@login_required
def ta_rules_view():
    return "rules"

@app.route('/ta/rules/update')
@login_required
def ta_rules_update():
    return "update"