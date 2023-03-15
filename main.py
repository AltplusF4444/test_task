import os
import httpx
from dadata import Dadata
import keyboard
from threading import Thread
from getch import pause
import sqlite3

val = [True]


def thread(my_func):
    def wrapper(*args, **kwargs):
        any_thread = Thread(target=my_func, args=args, kwargs=kwargs)
        any_thread.setDaemon(True)
        any_thread.start()

    return wrapper


def Exit(event):
    print("Bye!")
    val[0] = False


class Cmd:
    token = ""
    query = ""
    language = ""

    @thread
    def login_window(self):
        try:
            conn = sqlite3.connect('DB.sqlite')
            cursor = conn.cursor()
        except sqlite3.Error as error:
            print(error)
            val[0] = False
            return

        cursor.execute("select * from settings")
        result = cursor.fetchone()

        self.token = result[0]
        self.language = result[1]

        os.system('cls')
        if self.token == "" or self.token is None:
            while self.token == "" or self.token is None:
                self.token = input("Введите или вставьте API-ключ Dadata (Escape - выход из программы)\n")

            try:
                dadata = Dadata(self.token)
                result = dadata.suggest("address", "москва")
                dadata.close()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403:
                    os.system('cls')
                    print("В запросе указан несуществующий API-ключ\nИли не подтверждена почта\nИли исчерпан дневной "
                          "лимит по количеству запросов")
                    pause("Нажмите любую кнопку, чтобы выйти")
                    val[0] = False
                elif e.response.status_code == 401:
                    os.system('cls')
                    print("В запросе отсутствует API-ключ")
                    pause("Нажмите любую кнопку, чтобы выйти")
                    val[0] = False
            else:
                save = ""
                while save != "1" and save != "2":
                    os.system('cls')
                    save = input("Хотите сохранить вход?\n1 - да\n2 - нет\nEsc - закрыть приложение\n")
                if save == "1":
                    try:
                        cursor.execute('''update settings set token = ?, language = ? where id = 1''',
                                       (self.token, self.language))
                        conn.commit()
                    except sqlite3.Error as error:
                        print(error)

                self.commands_window()
                return
        else:
            self.commands_window()
            return

    @thread
    def commands_window(self):
        var = ""
        while var != "1" and var != "2" and var != "3":
            os.system('cls')
            var = str(input("Здравствуйте! Выберите действие\n1 - Выполнить поиск координат по адресу\n2 - "
                            "Поменять язык результата поиска\n3 - Выйти из аккаунта\nEsc - закрыть приложение\n"))
            if var == "1":
                self.search()
            elif var == "2":
                self.set_lang()
            elif var == "3":
                self.logout()

    @thread
    def search(self):
        os.system('cls')
        query = input("Введите желаемый адрес: ")
        dadata = Dadata(self.token)
        results = dadata.suggest("address", query, count=20, language=self.language)
        i = 1
        lst = {}
        for result in results:
            print(str(i) + " - " + str(result['value']))
            lst[str(i)] = str(result['value'])
            i += 1

        query = input("Выберите вариант из предложенных значений: ")
        while lst.get(query) is None:
            query = input("Введено неправильное число!\nВыберите вариант из предложенных значений: ")
        result = dadata.suggest("address", lst.get(query), count=1, language=self.language)
        print("Адрес: " + lst.get(query))
        print("Широта: " + str(result[0]['data']['geo_lat']))
        print("Долгота: " + str(result[0]['data']['geo_lon']))
        var = ""
        while var != "1" and var != "2":
            var = input("Хотите повторить поиск?\n1 - да\n2 - вернуться в главное меню\nEsc - закрыть приложение\n")
        if var == "1":
            self.search()
        elif var == "2":
            self.commands_window()

    @thread
    def set_lang(self):
        var = ""
        try:
            conn = sqlite3.connect('DB.sqlite')
            cursor = conn.cursor()
        except sqlite3.Error as error:
            print(error)
            val[0] = False
            return

        while var != "1" and var != "2":
            os.system('cls')
            var = str(input("Выберите язык:\n1 - Русский\n2 - Английский\nEsc - закрыть приложение\n"))
        if var == "1":
            self.language = "ru"
        elif var == "2":
            self.language = "en"
        try:
            cursor.execute('''update settings set language = ? where id = 1''',
                           (self.language,))
            conn.commit()
        except sqlite3.Error as error:
            print(error)
            val[0] = False
            return
        self.commands_window()

    @thread
    def logout(self):
        self.token = ""
        try:
            conn = sqlite3.connect('DB.sqlite')
            cursor = conn.cursor()
        except sqlite3.Error as error:
            print(error)
            val[0] = False
            return
        try:
            cursor.execute('''update settings set token = ? where id = 1''',
                           (self.token,))
            conn.commit()
        except sqlite3.Error as error:
            print("2 " + str(error))
            val[0] = False
            return
        self.login_window()


if __name__ == '__main__':
    keyboard.on_press_key("esc", callback=Exit)

    cmd = Cmd()
    cmd.login_window()
    while val[0]:
        pass
