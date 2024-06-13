# Database interactions

# database.py
import sqlite3

class DatabaseManager:
    def __init__(self, db_name="chatbot.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_user_table()

    def create_user_table(self):
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT
        )
        '''
        self.conn.execute(create_table_query)

    def add_user(self, name, email):
        insert_query = 'INSERT INTO users (name, email) VALUES (?, ?)'
        self.conn.execute(insert_query, (name, email))
        self.conn.commit()

    def get_user(self, name):
        query = 'SELECT * FROM users WHERE name = ?'
        user = self.conn.execute(query, (name,)).fetchone()
        return user
