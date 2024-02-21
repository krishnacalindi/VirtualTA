from flask import render_template, url_for, request
from flaskr import app
from flaskr.forms import LoginForm, RegisterForm

@app.route('/')
def welcome():
    return render_template('welcome.html', title="Welcome")

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return "got form"
    form = LoginForm()
    return render_template('auth/login.html', title="LogIn", form=form)

@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return "got form"
    form = RegisterForm()
    return render_template('auth/register.html', title="Register", form=form)