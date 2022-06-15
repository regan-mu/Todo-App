from flask_wtf import FlaskForm
from wtforms import TextAreaField, TimeField, DateField, StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length


class TodoList(FlaskForm):
    list_name = StringField('Title', validators=[DataRequired(), Length(max=15)])
    list_description = TextAreaField('Description', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Create List')


class Signup(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=10)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')


class Login(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class Tasks(FlaskForm):
    task_name = StringField('Task', validators=[DataRequired(), Length(max=50)])
    due_date = DateField('Due Date', validators=[DataRequired()])
    due_time = TimeField('Due Time', validators=[DataRequired()])
    submit = SubmitField('Add Task')
