from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FileField, DateTimeField, TimeField
from wtforms.validators import DataRequired, Length, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    full_name = StringField('Full Name', validators=[Optional(), Length(max=100)])
    role = SelectField('Role', choices=[('student', 'Siswa'), ('sensei', 'Guru')], validators=[DataRequired()])
    class_id = SelectField('Class', coerce=int, validators=[Optional()])

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    new_password_confirm = PasswordField('Confirm New Password', validators=[DataRequired()])

class PublicRegisterForm(FlaskForm):
    full_name = StringField('Nama Lengkap', validators=[DataRequired(), Length(min=3, max=100)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password_confirm = PasswordField('Konfirmasi Password', validators=[DataRequired(), Length(min=6)])
    email = StringField('Email', validators=[Optional(), Length(max=100)])
    phone = StringField('Nomor Telepon', validators=[Optional(), Length(max=20)])
    address = TextAreaField('Alamat', validators=[Optional()])

class MaterialForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=255)])
    content = TextAreaField('Content', validators=[DataRequired()])
    file = FileField('File', validators=[Optional()])

class QuizForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=255)])

class AssignmentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description', validators=[DataRequired()])
    due_date = DateTimeField('Due Date', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    file = FileField('File', validators=[Optional()])

class ClassForm(FlaskForm):
    name = StringField('Class Name', validators=[DataRequired(), Length(max=100)])
    schedule = StringField('Schedule', validators=[Optional(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    start_time = TimeField('Start Time', format='%H:%M', validators=[Optional()])
    end_time = TimeField('End Time', format='%H:%M', validators=[Optional()])

class CertificateForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    certificate_number = StringField('Certificate Number', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    file = FileField('File', validators=[Optional()])

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FileField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    full_name = StringField('Full Name', validators=[Optional()])
    role = SelectField('Role', choices=[('student', 'Student'), ('sensei', 'Teacher'), ('admin', 'Admin')])

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    new_password_confirm = PasswordField('Confirm New Password', validators=[DataRequired()])