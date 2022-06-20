import os

class Controller:

    # Получить главы книги
    def get_chapters(self, author_fullname: str, book_title: str) -> list:
        chapters = []
        for chapter in os.listdir(os.path.join(os.getcwd(), "static", "authors", author_fullname, book_title)):
            chapters.append(chapter)

        return chapters


    # Получить текст книги
    def get_book_text(self, author_fullname: str, book_title: str, chapter_active: str) -> str:
        book_text = ""
        with open(os.path.join(os.path.join(os.getcwd(), "static", "authors", author_fullname, book_title, chapter_active)), encoding="utf-8", mode="r") as html_file:
            book_text = html_file.read()

        return book_text
