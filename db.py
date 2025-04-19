import mysql.connector
from mysql.connector import errorcode
import bcrypt

class Database:
    def __init__(self):
        self.config = {
            'user': 'medisave_user',
            'password': 'Pass123!',
            'host': '127.0.0.1',
            'database': 'medisave',
            'raise_on_warnings': True,
        }
        self.conn = None
    
    def connect(self):
        try:
            self.conn = mysql.connector.connect(**self.config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Invalid credentials")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            raise
    
    def close(self):
        if self.conn:
            self.conn.close()

    def create_user(self, email, password):
        cursor = self.conn.cursor()
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, %s)",
            (email, password_hash)
        )
        self.conn.commit()
        cursor.close()

    def authenticate(self, email, password):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, password_hash FROM users WHERE email=%s",
            [email]
        )
        row = cursor.fetchone()
        cursor.close()
        if bcrypt.checkpw(password.encode(), row[1].encode()):
            return row[0]
        else:
            return None

