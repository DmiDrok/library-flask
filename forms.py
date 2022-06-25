from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Email, Length, EqualTo, DataRequired


# Форма регистрации
class RegForm(FlaskForm):
    email = StringField(label="Почта:", validators=[DataRequired(message="Введите почту!"), Email(message="Здесь должа быть почта!")], render_kw={"placeholder": "Ваша почта"})
    password = PasswordField(label="Пароль:", validators=[DataRequired(message="Введите пароль!")], render_kw={"placeholder": "Ваш пароль"})
    password_again = PasswordField(label="Повторите пароль:", validators=[DataRequired(message="Повторите пароль!"), EqualTo("password", message="Пароли не совпадают!")], render_kw={"placeholder": "Пароль ещё раз"})
    submit = SubmitField(label="Регистрация")


# Форма авторизации
class AuthForm(FlaskForm):
    email = StringField(label="Почта:", validators=[DataRequired(message="Введите почту!"), Email(message="Здесь должна быть почта!")], render_kw={"placeholder": "Ваша почта"})
    password = PasswordField(label="Пароль:", validators=[DataRequired(message="Введите пароль!")], render_kw={"placeholder": "Ваша пароль"})
    submit = SubmitField(label="Авторизация")