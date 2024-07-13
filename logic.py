import sqlite3
from config import DATABASE
import json

class DB_Manager:
    def __init__(self, database):
        self.database = database
        
    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE users (
                            user_id INTEGER PRIMARY KEY,
                            anime_list TEXT
                        )''') 

            conn.commit()

    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()
    
    def __select_data(self, sql, data = tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()


    def search_anime(self, data, value):
        if data == "staff":
            sql = f"SELECT * FROM anime WHERE {data} LIKE '%{value} : Chief Director%' OR {data} LIKE '%{value} : Director%' LIMIT 10"
            result = self.__select_data(sql)
            return result
        elif data == "Tags":
            value = value.split(",")
            conditions = []
            for tag in value:
                conditions.append(f"{data} LIKE '%{tag.strip()}%'")

            sql_condition = " AND ".join(conditions)
            sql = f"SELECT * FROM anime WHERE {sql_condition} LIMIT 10"
            result = self.__select_data(sql)
            return result
        elif data == "Name":
            sql = f"SELECT * FROM anime WHERE Name LIKE '%{value}%' OR Japanese_name LIKE '%{value}%' LIMIT 10"
            result = self.__select_data(sql)
            return result
        else:
            sql = f"SELECT * FROM anime WHERE {data} = '{value}' LIMIT 10"
            result = self.__select_data(sql)
            return result
        
    def add_anime_to_list(self, user_id, anime_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('SELECT anime_list FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()

            if result is not None:
                current_list = json.loads(result[0])
            else:
                current_list = []

            current_list.append(anime_id)
            updated_list_json = json.dumps(current_list)

            conn.execute('INSERT OR REPLACE INTO users (user_id, anime_list) VALUES (?, ?)', (user_id, updated_list_json))
            conn.commit()

    def anime_exists_for_user(self, user_id, anime_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('SELECT anime_list FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()

            if result and result[0] is not None:
                current_list = json.loads(result[0])
                if anime_id in current_list:
                    return True
            return False

    def get_anime_list(self, user_id):
        sql = "SELECT anime_list FROM users WHERE user_id = ?"
        result = self.__select_data(sql, (user_id,))
        return result
        
        
if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
