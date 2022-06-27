from flask import Flask, render_template, g, url_for, request, flash, get_flashed_messages, redirect, jsonify, render_template_string, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user


from werkzeug.security import generate_password_hash, check_password_hash


from config import Config
from forms import RegForm, AuthForm


from itsdangerous import URLSafeTimedSerializer


from pretty_control import Controller


import logging
import threading
import os
import re


# Настройка логгирования
# logging.basicConfig(filename="logs.log", level=logging.ERROR)


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
login_manager.login_view = "register"

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
    portrait = db.Column(db.LargeBinary)
    biography_text = db.Column(db.Text)


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
    content = db.Column(db.Text)
    # type = db.Column(db.Text)


    def __repr__(self):
        return f"<Book {self.id}: {self.title} - Author: {self.author_id}>"


# Модель базы данных избранного у пользователей
class Favourites(db.Model):

    __tablename__ = "favourites"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)

    pr_author = db.relationship("Authors", backref="authors")
    pr_book = db.relationship("Books", backref="books")


    def __repr__(self):
        return f"<Favourite: {self.id} user_id: {self.user_id}, author_id: {self.author_id}, book_id: {self.book_id}>"


# Функция отправки сообщения на почту пользователю
def send_mail(subject: str, sender: str, recipients: list, text: str, confirm_link=None) -> bool:
    msg = Message(subject=subject, sender=sender, recipients=recipients)
    msg.html = text

    with app.app_context():
        mail.send(msg)


# Действия перед каждым запросом
@app.before_request
def before_request():

    if not hasattr(g, "Controller"):
        g.Controller = Controller()


# Создание папок с книгами
def create_folders():

    # Если папки с авторами нет - мы её создаём
    if not os.path.exists(os.path.join(os.getcwd(), "static", "authors")):
        os.mkdir(os.path.join(os.getcwd(), "static", "authors"))

    # Пробегаемся по каждому автору в Базе Данных
    for author in Authors.query.all():

        # Создаем папку с автором
        if str(author.fullname) not in os.listdir(os.path.join(os.getcwd(), "static", "authors")):
            os.mkdir(os.path.join(os.getcwd(), "static", "authors", str(author.fullname)))

        # Создаём подпапки
        for under_folder in ["Сочинения"]:
            if under_folder not in os.listdir(os.path.join(os.getcwd(), "static", "authors", str(author.fullname))):
                os.mkdir(os.path.join(os.getcwd(), "static", "authors", str(author.fullname), under_folder))

            if under_folder == "Сочинения":
                # Создаём папку с книгой
                for book in Books.query.filter_by(author_id=author.id).all():
                    try:
                        if str(book.title) not in os.listdir(os.path.join(os.getcwd(), "static", "authors", str(author.fullname), under_folder)):
                            os.mkdir(os.path.join(os.getcwd(), "static", "authors", str(author.fullname), under_folder, str(book.title)))
                    except Exception as err:
                        print(f"---Ошибка при создании папки книги с именем {book.title}---")


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
        url_for("favourites"): "default",
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

    all_authors = Authors.query.order_by(Authors.id.asc()).all() # Берём всех авторов по возрастанию поля id

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

                # Отправляем сообщение в отдельном потоке
                thread_send_mail = threading.Thread(target=send_mail, args=("Подтверждение почты на сайте 'Библиотека Марксизма'", app.config["MAIL_USERNAME"], [email,], f"<h3>Подтвердите свою почту пройдя по следующей ссылке: {url_for('confirm', token=token, _external=True)}</h3>", confirm_link))        
                thread_send_mail.start()
                thread_send_mail.join()

                print(f"Сообщение отправлено на почту {email}")



                flash("На вашу почту было отправлено письмо для подтверждения аккаунта", category="success")
                return redirect(url_for("register"))
            else:
                flash("Такая почта уже использована на сайте!", category="error")

        #else:
            #logging.error(msg=f"Пользователь {request.remote_addr} допустил ошибку при регистрации.")
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
        print(err)
        # logging.error(f"<У пользователя {request.remote_addr} произошла ошибка при подтверждении учётной записи>")

    user = Users.query.filter_by(email=email).first()
    user.confirm = True
    db.session.add(user)
    db.session.commit()

    return render_template("confirm.html")


# Обработчик страницы автора
@app.route("/author/<author_url>")
def author_page(author_url):
    author = Authors.query.filter_by(url=author_url).first()
    biography_text = author.biography_text
    all_books_default = Books.query.filter_by(author_id=author.id).order_by(Books.year.asc()).order_by(Books.year.asc()).all()
    
    all_books = {}
    for book in all_books_default:
        if book.year not in all_books:
            all_books[book.year] = []

        all_books[book.year].append(book)


    print(all_books)

    favourites_books = None
    if current_user.is_authenticated:
        favourites_books = Favourites.query.with_entities(Favourites.book_id).filter_by(user_id=current_user.id).all() if current_user.is_authenticated else None
        favourites_books = [x[0] for x in favourites_books]
        


    return render_template(
        "author.html", 
        author=author, 
        all_books=all_books, 
        favourites_books=favourites_books,
        biography_text=biography_text,
    )


# Обработчик страницы книги (на которой её главы и прочее)
@app.route("/author/<author_url>/book/<path:book_url>")
def book_page(author_url, book_url):
    author = Authors.query.filter_by(url=author_url).first()
    book = Books.query.filter_by(url=book_url).first()

    chapters = g.Controller.get_chapters(author_fullname=author.fullname, book_title=book.title)
    book_begin_text = Books.query.filter_by(title=book.title).first().content

    return render_template("book.html", author=author, book=book, chapters=chapters, book_begin_text=book_begin_text)


# Обработчик страницы с главой книги
@app.route("/author/<author_url>/book/<path:book_url>/<path:chapter_active>")
def book_chapter_page(author_url, book_url, chapter_active):
    author = Authors.query.filter_by(url=author_url).first()
    book = Books.query.filter_by(url=book_url).first()

    chapters = g.Controller.get_chapters_navigation(author_fullname=author.fullname, book_title=book.title)
    book_text = g.Controller.get_book_text(author_fullname=author.fullname, book_title=book.title, chapter_active=chapter_active)
    book_text = render_template_string(book_text, author=author, book=book, chapters_this_book=chapters)
    
    return render_template("book_content.html", author=author, book=book, chapter_active=chapter_active, chapters=chapters, book_text=book_text)


# Обработчик страницы с избранными произведениями
@app.route("/favourites")
@login_required
def favourites():
    reset_all_save_one(url_for("favourites"))


    all_favourites = Favourites.query.filter_by(user_id=current_user.id).all()
    
    all_books = {}

    for author in all_favourites:
        all_books[author.pr_author] = []

    for i in range(len(all_favourites)):
        for j in all_books:
            if all_favourites[i].pr_author == j:
                all_books[j].append(all_favourites[i])
    

    return render_template("favourites.html", links=g.links, all_favourites=all_books)


# Принимаем избранное и кладём в БД
@app.route("/favourites/upload", methods=["POST", "GET"])
@login_required
def favourites_upload():
    response = request.json
    content_add = response.get("add").get("content")
    content_remove = response.get("remove").get("content")
    author_fullname = response.get("author")

    all_favourites_books = [book.pr_book.title for book in Favourites.query.filter_by(user_id=current_user.id).all()]

    # Алгорит добавления в избранное
    for book in content_add:
        if book not in all_favourites_books:     
            b = Favourites(
                user_id=current_user.id,
                author_id=Authors.query.filter_by(fullname=author_fullname).first().id,
                book_id=Books.query.filter_by(title=book).first().id
            )

            db.session.add(b)
            db.session.commit()



    # Алгоритм удаления из избранного
    for book in content_remove:
        Favourites.query.filter_by(book_id=Books.query.filter_by(title=book).first().id).delete()

    db.session.commit()


    return f"{all_favourites_books}"


# Обработчик получения портрета автора
@app.route("/get_author_portrait/<id>")
def get_author_portrait(id):
    content = Authors.query.filter_by(id=id).first().portrait
    response = make_response(content, 200)

    response.headers["Content-type"] = "img/jpg"
    return response


# Точка входа
if __name__ == "__main__":
    app.run(debug=True)