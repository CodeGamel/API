import mysql.connector
from mysql.connector import Error
def connection():
    connection = None  
    try:
        conn= mysql.connector.connect(
        database = 'LA_FITNESS',
        user = 'root',
        password = 'lolol',
        host = 'localhost'
        )
        if conn.is_connected():
            print("Successfully connected to the database")
            return conn
    except Error as e:
        print(f"Error : {e}")
        return ("Could not connect.")

