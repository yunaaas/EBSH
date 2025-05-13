import sqlite3
import pandas as pd
import requests


class UserDB:
    def __init__(self, db_name="users.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            phone TEXT DEFAULT NULL,
            registration_date TEXT DEFAULT (datetime('now', 'localtime'))
        )
        ''')
        self.conn.commit()

    def add_user(self, user_id, first_name, last_name, username, phone=None):
        """Добавляет пользователя в базу данных с возможностью указать дату рождения"""
        self.cursor.execute("INSERT INTO users (user_id, first_name, last_name, username, phone) VALUES (?, ?, ?, ?, ?)",
                            (user_id, first_name, last_name, username, phone))
        self.conn.commit()

    def get_user(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        result = self.cursor.fetchone()
        return result if result else None

    def add_user_if_not_exists(self, user_id, first_name, last_name, username, phone=None):
        """Проверяет, существует ли пользователь, и если нет, добавляет его в базу данных"""
        if not self.get_user(user_id):
            self.add_user(user_id, first_name, last_name, username, phone)


    def get_id(self):
        """Возвращает список всех user_id из базы данных"""
        self.cursor.execute("SELECT user_id FROM users")
        return self.cursor.fetchall()
    
    def get_all_users(self):
        """Возвращает список всех пользователей с их данными"""
        self.cursor.execute("SELECT user_id, first_name, last_name, username, phone, registration_date FROM users")
        return self.cursor.fetchall()  # Возвращаем все данные о пользователях в виде списка кортежей


    def set_dr(self, id, data):
        self.cursor.execute('UPDATE users SET phone = ? WHERE user_id = ?', (data, id))
        self.conn.commit()
        return True
    


    def get_all_users(self):
        """Возвращает список всех пользователей с их данными"""
        self.cursor.execute("SELECT user_id, first_name, last_name, username, phone, registration_date FROM users")
        return self.cursor.fetchall()  # Возвращаем все данные о пользователях в виде списка кортежей

    def export_to_excel(self, filename="users_data.xlsx"):
        """Экспортирует данные пользователей в Excel файл"""
        # Получаем все данные пользователей
        users = self.get_all_users()

        # Создаем DataFrame из полученных данных
        df = pd.DataFrame(users, columns=["user_id", "first_name", "last_name", "username", "phone", "registration_date"])

        # Экспортируем в Excel
        df.to_excel(filename, index=False)
        print(f"Данные успешно экспортированы в {filename}")



    def upload_file_to_yandex_disk(self, token, local_file_path, file_path_on_disk):
        """
        Функция для загрузки файла на Яндекс.Диск.

        :param token: OAuth токен для Яндекс.Диска
        :param local_file_path: Путь к локальному файлу для загрузки
        :param file_path_on_disk: Путь на Яндекс.Диске, куда нужно загрузить файл
        :return: None
        """
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'

        headers = {
            'Authorization': f'OAuth {token}'
        }

        params = {
            'path': file_path_on_disk,
            'overwrite': 'true'
        }

        # Получаем ссылку для загрузки
        response = requests.get(upload_url, headers=headers, params=params)

        if response.status_code == 200:
            upload_link = response.json().get('href')
            print(f'Ссылка для загрузки: {upload_link}')

            # Загружаем файл
            with open(local_file_path, 'rb') as file:
                upload_response = requests.put(upload_link, headers=headers, files={'file': file})

            if upload_response.status_code == 201:
                print('Файл успешно загружен на Яндекс.Диск!')
            else:
                print(f'Ошибка при загрузке файла: {upload_response.status_code}')
        else:
            print(f'Ошибка при получении ссылки для загрузки: {response.status_code}')