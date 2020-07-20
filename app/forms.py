from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, HiddenField
from wtforms_components import TimeField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length, NoneOf
from app.models import User
from flask_wtf.recaptcha import RecaptchaField


class AnnouncementForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[
        DataRequired(), Length(min=0, max=400)],
        default="Welcome to our amazing Lunch Roulette service!")
    submit = SubmitField('Send Announcement')

class InviteForm(FlaskForm):
    firstname = StringField('Firstname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[
        DataRequired(), Length(min=0, max=140)], default="this amazing!\
 service can improve our communication and agility company wide!")
    submit = SubmitField('Send Invite')

class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[
        DataRequired(), Length(min=0, max=140)])
    submit = SubmitField('Submit')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    #recaptcha = RecaptchaField()
    submit = SubmitField('Request Password Reset')

class EditProfileForm(FlaskForm):
    username = StringField('Username (ideally: short, memorable, no spaces)',
        validators=[DataRequired(), Length(min=0, max=32), NoneOf(['now'])])
    about_me = TextAreaField('About me (free text)',
        validators=[Length(min=0, max=140)])
    topics = TextAreaField('Topics (please use keywords separated by space)',
        validators=[Length(min=0, max=140)])
    lunch_time = TimeField('I usually go for lunch at (HH:MM)',
        validators=[DataRequired()])
    invite_me = BooleanField('Every workday, invite me for lunch, if there\'s a match')
    site = StringField('What\'s your company\'s Site name or nearby City',
        validators=[Length(min=0, max=32), DataRequired()])
    canteen = StringField('Canteen (an empty value means: ALL at your Site)',
        validators=[Length(min=0, max=32)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class RegistrationForm(FlaskForm):
    username = StringField('Username (ideally: short, memorable, no spaces)',
        validators=[DataRequired(), NoneOf(['now'])])
    email = StringField('E-mail (please use & enter your corporate e-mail)',
        validators=[DataRequired(), Email()])
    lunch_time = TimeField('I usually go for lunch at (HH:MM)',
        validators=[DataRequired()])
    invite_me = BooleanField('Every workday, invite me for lunch, if there\'s a match')
    site = StringField('What\'s your company\'s Site name or nearby City',
        validators=[Length(min=0, max=32), DataRequired()])
    canteen = StringField('Canteen (an empty value means: ALL at your Site)',
        validators=[Length(min=0, max=32)])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    #recaptcha = RecaptchaField()
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    #recaptcha = RecaptchaField()
    timezone = HiddenField(validators=[DataRequired(
        message = "Sorry, we could not detect your timezone from your browser!"
    )])
    submit = SubmitField('Sign In')
