from dotenv import load_dotenv


import os


# Грузим переменные окружения
venv_path = os.path.join(os.getcwd(), ".env")
if os.path.exists(venv_path):
    load_dotenv(venv_path)


# Класс с конфигурацией
class Config:
    SECRET_KEY = "so0da-fsadfj1f0-2jfew9ajfsdajfasdf043-0tr1-1jkfosdjfasdf-012iet042jjsadf"
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:lokisqlpass@localhost/library"
    SQLALCHEMY_DATABASE_URI = "postgresql://ywyiacexzygcsx:97ec91892633bc75c977e1cb5a33d94898c8b25dda90cf8e47219c22aec2d714@ec2-34-248-169-69.eu-west-1.compute.amazonaws.com:5432/d4d4mre08o4q87"
    #SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = "smtp.mail.ru"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_USE_TLS = True
    MAIL_PORT = 587