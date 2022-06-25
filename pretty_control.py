import os

class Controller:

    # Получить главы книги
    def get_chapters(self, author_fullname: str, book_title: str) -> list:
        try:
            chapters = []
            listdir = sorted(os.listdir(os.path.join(os.getcwd(), "static", "authors", author_fullname, book_title)))
            for chapter in listdir:
                if "ind1" in chapter: # Если отступ уровня 1
                    chapters.append({"type": "ind1", "chapter_text": chapter})
                else: # Если отступов нет
                    chapters.append({"type": "default", "chapter_text": chapter})

            return chapters
        except:
            pass


    # Получить главы книги в виде списка (для навигации сверху и снизу)
    def get_chapters_navigation(self, author_fullname: str, book_title: str) -> list:
        try:
            chapters = []

            for chapter in os.listdir(os.path.join(os.getcwd(), "static", "authors", author_fullname, book_title)):
                chapters.append(chapter)

            return chapters
        except:
            pass


    # Получить текст книги
    def get_book_text(self, author_fullname: str, book_title: str, chapter_active: str) -> str:
        try:
            book_text = ""
            with open(os.path.join(os.path.join(os.getcwd(), "static", "authors", author_fullname, book_title, chapter_active)), encoding="utf-8", mode="r") as html_file:
                book_text = html_file.read()

            return book_text
        except:
            pass