from peewee import *
from flask_wtf import FlaskForm
from wtforms.validators import (DataRequired, ValidationError, Email, Regexp, Length, EqualTo)
from wtforms import StringField, PasswordField,TextAreaField
from models import User


##VALIDACIONES DE LOS DATOS DE ENTRADA

def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError("Ya existe un usuario con ese nombre")

def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError("Ya existe un correo igual, favor de cambiar")


class RegisterForm(FlaskForm):
    username = StringField(
        'Username',
        validators = [
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$'
            ),
            name_exists
        ]
    )
    email = StringField(
        'Email',
        validators = [
            DataRequired(),
            Email(),
            email_exists
        ]
    )
    password = PasswordField(
        'Password',
        validators = [
            DataRequired(),
            Length(min=8),
            EqualTo('password2', message="Las constaseñas deben coincidir")
        ]
    )
    password2 = PasswordField(
        'Confirm Password',
        validators = [
            DataRequired()
        ]
    )


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('password', validators=[DataRequired()])


class PostForm(FlaskForm):
    content = TextAreaField('¿QUE ESTAS PENSANDO?', validators=[DataRequired()])
