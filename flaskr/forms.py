from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, InputRequired
from flaskr import conn

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=15, message="Length of username must be 5-15 characters.")])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=15, message="Length of password must be 5-15 characters."), EqualTo('confirm', message="Passwords must match.")])
    confirm = PasswordField('Repeat password',  validators=[DataRequired(), Length(min=5, max=15, message="Length of password must be 5-15 characters.")])
    submit = SubmitField('Register')
    def validate_password(self, password):
        lowercaseVal = False
        uppercaseVal = False
        specialcharVal = False
        specialChars = "[@_!#$%^&*()<>?/\|}{~:]"
        for c in password.data:
            if c.islower():
                lowercaseVal = True
            elif c.isupper():
                uppercaseVal = True
            else:
                for specialChar in specialChars:
                    if specialChar == c:
                        specialcharVal = True
        if not (lowercaseVal and uppercaseVal and specialcharVal):
            raise ValidationError('Not a strong password.')
    def validate_username(self, username):
        cursor = conn.cursor()
        validate_username_command = "SELECT * FROM user_info WHERE username = ?;"
        username = str(username)
        cursor.execute(validate_username_command, (username,))
        user_data = cursor.fetchone()
        if user_data is not None:
            raise ValidationError('Please use a different username.')
    def validate_email(self, email):
        cursor = conn.cursor()
        validate_email_command = "SELECT * FROM user_info WHERE email = ?;"
        email = str(email)
        cursor.execute(validate_email_command, (email,))
        user_data = cursor.fetchone()
        if user_data is not None:
            raise ValidationError('Please use a different email.')

class DFAForm(FlaskForm):
    otp = StringField('Secret code', validators=[DataRequired()])
    submit = SubmitField('Authenticate')

class SyllabusForm(FlaskForm):
    syllabus = FileField('Upload syllabus', validators=[InputRequired()])
    submit = SubmitField('Upload')
