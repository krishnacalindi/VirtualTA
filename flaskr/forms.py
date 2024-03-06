from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=15, message="Length of username must be 4-15 characters.")])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=15, message="Length of password must be 4-15 characters."), EqualTo('confirm', message="Passwords must match.")])
    confirm = PasswordField('Repeat password',  validators=[DataRequired(), Length(min=5, max=15, message="Length of password must be 4-15 characters.")])
    submit = SubmitField('Register')
    def validate_password(self, password):
        lowercaseVal = False
        uppercaseVal = False
        specialcharVal = False
        specialChars = '[@_!#$%^&*()<>?/\|}{~:]'
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
            raise ValidationError('Not a strong password')

class DFAForm(FlaskForm):
    otp = StringField('Secret code', validators=[DataRequired()])
    submit = SubmitField('Authenticate')