from flask import render_template, url_for, request, redirect
from flaskr import app, mail
from flaskr.forms import LoginForm, RegisterForm, DFAForm
from flask_mail import Message

@app.route('/')
def welcome():
    return render_template('welcome.html', title="Welcome")

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('sendmail'))
    form = LoginForm()
    return render_template('auth/login.html', title="LogIn", form=form)

@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return "got form"
    form = RegisterForm()
    return render_template('auth/register.html', title="Register", form=form)

@app.route('/auth/logout')
def logout():
    return redirect(url_for('welcome'))

@app.route('/auth/sendmail')
def sendmail():
    mail_message = Message('Test', sender=app.config['MAIL_USERNAME'], recipients=['krishnacalindi@outlook.com'])
    mail_message.body = 'Testing to see whether this works!'
    mail.send(mail_message)
    return redirect(url_for('dfa')) 

@app.route('/auth/dfa', methods=['GET', 'POST'])
def dfa():
    if request.method == 'POST':
        return "got dfa"
    form = DFAForm()
    return render_template('auth/dfa.html', title="Dual Factor Authentication", form=form)