from flask import Flask, render_template, g, url_for, request, flash, get_flashed_messages, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user


from werkzeug.security import generate_password_hash, check_password_hash


from config import Config
from forms import RegForm, AuthForm


from itsdangerous import URLSafeTimedSerializer


import logging
import threading
import os
import re


# Настройка логгирования
logging.basicConfig(filename="logs.log", level=logging.ERROR)


# WSGI - приложение
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.from_object(Config)


# База данных
db = SQLAlchemy(app)

# Для миграции базы данных
migrate_manager = Migrate(app, db)

# С помощью него будем подтверждать почту пользователя
Serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# Отправка сообщений на почту пользователю
mail = Mail(app)

# Логин - менеджер
login_manager = LoginManager(app)
@login_manager.user_loader
def upload_user(id):
    return Users.query.filter_by(id=id).first()

# Модель базы данных (таблица) пользователей
class Users(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    confirm = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<User {self.id}: {self.email}>"


# Модель базы данных авторов
class Authors(db.Model):

    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.Text, unique=True, nullable=False)
    url = db.Column(db.Text, unique=True, nullable=False)
    years_life = db.Column(db.Text, nullable=False, default="?")


    def __repr__(self):
        return f"<Author {self.id}: {self.fullname}>"


# Модель базы данных книг
class Books(db.Model):

    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, unique=True, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), nullable=False)
    url = db.Column(db.Text, unique=True, nullable=False)
    year = db.Column(db.Integer)


    def __repr__(self):
        return f"<Book {self.id}: {self.title} - Author: {self.author_id}>"


# Создание папок с книгами
def create_folders():
    for author in Authors.query.all():
        if str(author.fullname) not in os.listdir(os.path.join(os.getcwd(), "static", "authors")):
            os.mkdir(os.path.join(os.getcwd(), "static", "authors", str(author.fullname)))

            for book in Books.query.filter_by(author_id=author.id).all():
                os.mkdir(os.path.join(os.getcwd(), "static", "authors", str(author.fullname), str(book.title)))

                # Тут главы можно делать потом
                #with open(os.path.join(os.getcwd(), "static", "authors", str(author.fullname), str(book.title)), encoding="utf-8", mode="w") as file:
                    #pass

# Сделать одну из ссылок активной
def reset_all_save_one(save):
    for btn in g.links:
        g.links[btn] = "default"

    g.links[save] = "active"


# До каждого запроса
@app.before_request
def before_request():
    # Ссылки на сайте
    links = {
        url_for("index"): "default",
        url_for("all_authors"): "default",
        url_for("about"): "default",
        url_for("auth"): "default",
        url_for("register"): "default",
    }

    if not hasattr(g, "links"):
        g.links = links


# Обработчик главной страницы
@app.route("/")
def index():
    reset_all_save_one(url_for("index"))
    return render_template("index.html", links=g.links)


# Обработчик страницы со всеми книгами
@app.route("/all_authors")
def all_authors():
    reset_all_save_one(url_for("all_authors"))

    all_authors = Authors.query.all()

    return render_template("all_authors.html", links=g.links, all_authors=all_authors)


# Обработчик страницы 'О сайте'
@app.route("/about")
def about():
    reset_all_save_one(url_for("about"))
    return render_template("about.html", links=g.links)


# Обработчик страницы с регистрацией
@app.route("/register", methods=["POST", "GET"])
def register():
    reset_all_save_one(url_for("register"))

    form = RegForm()
    if request.method == "POST":
        if form.validate_on_submit():
            email = form.email.data
            password = generate_password_hash(form.password.data)

            user = Users.query.filter_by(email=email).first()
            
            if user is None:
                user = Users(
                    email=email,
                    password=password,
                    confirm=False
                )

                db.session.add(user)
                db.session.commit()

                token = Serializer.dumps(email, salt="email_confirm") # Создаём token, который вставим в url. Первый аргумент - что будет зашифровано (потом это вытащим при подтверждении)
                confirm_link = url_for("confirm", token=token, _external=True) # Ссылка для подтверждения (её получит пользователь)

                msg = Message(subject="Подтверждение почты на сайте 'БиблиоМаркс'", sender=app.config["MAIL_USERNAME"], recipients=[email])
                msg.html = f"<h3>Подтвердите свою почту по этой ссылке: {confirm_link}</h3>"

                mail.send(msg) # Отправляем пользователю сообщение на почту

                flash("На вашу почту было отправлено письмо для подтверждения аккаунта", category="success")
                return redirect(url_for("register"))
            else:
                flash("Такая почта уже использована на сайте!", category="error")

        else:
            logging.error(msg=f"Пользователь {request.remote_addr} допустил ошибку при регистрации.")
            #flash("Ошибка при заполнении формы...", category="error")


    return render_template("register.html", links=g.links, form=form)


# Обработчик страницы с авторизацией
@app.route("/auth", methods=["POST", "GET"])
def auth():
    reset_all_save_one(url_for("auth"))

    form = AuthForm()

    if request.method == "POST":
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data

            user = Users.query.filter_by(email=email).first()

            if user:
                if check_password_hash(user.password, password):
                    if user.confirm:
                        login_user(user) # Регистрируем пользователя
                        return redirect(url_for("index"))
                    else:
                        flash("Пользователь не подтверждён.", category="error")
                else:
                    flash("Ошибка при вводе данных.", category="error")
            else:
                flash("Пользователь не найден.", category="error")
                

    return render_template("auth.html", links=g.links, form=form)


# Обработчик для подтверждения страницы
@app.route("/confirm/<token>")
def confirm(token):
    try:
        email = Serializer.loads(token, salt="email_confirm", max_age=100) # Достаём из токена email, который шифровали
    except Exception as err:
        logging.error(f"<У пользователя {request.remote_addr} произошла ошибка при подтверждении учётной записи>")

    user = Users.query.filter_by(email=email).first()
    user.confirm = True
    db.session.add(user)
    db.session.commit()

    return render_template("confirm.html")


# Обработчик страницы автора
@app.route("/author/<author_url>")
def author_page(author_url):
    author = Authors.query.filter_by(url=author_url).first()
    all_books = Books.query.filter_by(author_id=author.id).all()

    return render_template("author.html", author=author, all_books=all_books)


# Обработчик страницы книги (на которой её главы и прочее)
@app.route("/author/<author_url>/book/<path:book_url>")
def book_page(author_url, book_url):
    author = Authors.query.filter_by(url=author_url).first()
    book = Books.query.filter_by(url=book_url).first()

    chapters = []
    for chapter in os.listdir(os.path.join(app.root_path, "static", "authors", str(author.fullname), str(book.title))):
        chapters.append(chapter)

    return render_template("book.html", author=author, book=book, chapters=chapters)

# Обработчик страницы с главой книги
@app.route("/author/<author_url>/book/<path:book_url>/<path:chapter_active>")
def book_chapter_page(author_url, book_url, chapter_active):
    author = Authors.query.filter_by(url=author_url).first()
    book = Books.query.filter_by(url=book_url).first()

    chapters = []
    for chap in os.listdir(os.path.join(app.root_path, "static", "authors", str(author.fullname), str(book.title))):
        chapters.append(chap)

    book_text = ""
    with open(os.path.join(os.path.join(app.root_path, "static", "authors", str(author.fullname), str(book.title), str(chapter_active))), encoding="utf-8", mode="r") as html_file:
        book_text = html_file.read()
    print(book_text)

    return render_template("book_content.html", author=author, book=book, chapter_active=chapter_active, chapters=chapters, book_text=book_text)

# Точка входа
if __name__ == "__main__":
    app.run(host="localhost", port=5005, debug=True)