import sqlite3
from datetime import datetime

class AdminDB:
    def __init__(self, db_name="admins.db"):
        """Инициализация подключения к базе данных"""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """Создание таблицы для хранения информации об администраторах"""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY,  -- Теперь это ID из Telegram
            name TEXT NOT NULL,
            comment TEXT DEFAULT NULL,
            date_added TEXT DEFAULT (datetime('now', 'localtime'))
        )
        ''')
        self.conn.commit()

    def add_admin(self, tg_id, name, comment=None):
        """Добавляет администратора в базу данных с его ID из Telegram"""
        self.cursor.execute("INSERT INTO admins (id, name, comment, date_added) VALUES (?, ?, ?, ?)",
                            (tg_id, name, comment, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.conn.commit()

    def get_all_admins(self):
        """Получить список всех администраторов"""
        self.cursor.execute("SELECT id, name, comment, date_added FROM admins")
        return self.cursor.fetchall()

    def get_admin_by_id(self, admin_id):
        """Получить информацию об администраторе по его Telegram ID"""
        self.cursor.execute("SELECT id, name, comment, date_added FROM admins WHERE id=?", (admin_id,))
        return self.cursor.fetchone()

    def update_admin_comment(self, admin_id, comment):
        """Обновить комментарий администратора по его Telegram ID"""
        self.cursor.execute("UPDATE admins SET comment=? WHERE id=?", (comment, admin_id))
        self.conn.commit()

    def delete_admin(self, admin_id):
        """Удалить администратора из базы данных по его Telegram ID"""
        self.cursor.execute("DELETE FROM admins WHERE id=?", (admin_id,))
        self.conn.commit()

    def close(self):
        """Закрыть соединение с базой данных"""
        self.conn.close()
