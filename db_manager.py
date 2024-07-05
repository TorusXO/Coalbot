import sqlite3
from app.Classes import Shisha

class DBManager:
    def __init__(self, db_name='mydatabase.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()


    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS shishas (
                id INTEGER PRIMARY KEY,
                table_id INTEGER,
                start_time REAL,
                chat_id INTEGER,
                coal_changes INTEGER DEFAULT 0,
                last_coal_change REAL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tables (
                id INTEGER PRIMARY KEY,
                name TEXT,
                floor INTEGER
            )
        ''')
                # Create a new table for user data
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY,
                current_table INTEGER,
                status_message TEXT,
                menu_message TEXT,
                total_shishas INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS total_shishas (
                total INTEGER
            )
        ''')
        self.cursor.execute('''
            INSERT INTO total_shishas (total)
            SELECT 0 WHERE NOT EXISTS(SELECT 1 FROM total_shishas)
        ''')
        self.conn.commit()
    
    def insert_shisha(self, table_id, start_time, chat_id, coal_changes):
        self.cursor.execute('''
            INSERT INTO shishas (table_id, start_time, chat_id, coal_changes)
            VALUES (?, ?, ?, ?)
        ''', (table_id, start_time, chat_id, coal_changes))
        self.conn.commit()
        return self.cursor.lastrowid  # Return the id of the inserted shisha
    def update_shisha(self, db_id, start_time, coal_changes, last_coal_change):
        self.cursor.execute('''
            UPDATE shishas
            SET start_time = ?, coal_changes = ?, last_coal_change = ?
            WHERE id = ?
        ''', (start_time, coal_changes, last_coal_change, db_id))
        self.conn.commit()

    def delete_shisha(self, db_id):
        self.cursor.execute('''
            DELETE FROM shishas
            WHERE id = ?
        ''', (db_id,))
        self.conn.commit()

    def get_shishas(self, table_id):
        self.cursor.execute('SELECT id, table_id, start_time, chat_id, coal_changes FROM shishas WHERE table_id = ?', (table_id,))
        return [Shisha(id=row[1], table_id=row[1], start_time=row[2], chat_id=row[3], coal_changes=row[4], db_id=row[0]) for row in self.cursor.fetchall()]

    def get_all_shishas(self):
        self.cursor.execute('SELECT * FROM shishas')
        return [Shisha(*row) for row in self.cursor.fetchall()]
    
    def get_tables(self):
        self.cursor.execute('SELECT * FROM tables')
        return self.cursor.fetchall()
    
    def get_total_shishas(self):
        self.cursor.execute('SELECT total FROM total_shishas')
        return self.cursor.fetchone()[0]

    def increment_total_shishas(self):
        self.cursor.execute('UPDATE total_shishas SET total = total + 1')
        self.conn.commit()
    def decrement_total_shishas(self):
        self.cursor.execute('UPDATE total_shishas SET total = total - 1')
        self.conn.commit()

    def reset_total_shishas(self):
        self.cursor.execute('UPDATE total_shishas SET total = 0')
        self.conn.commit()

    def close(self):
        self.conn.close()