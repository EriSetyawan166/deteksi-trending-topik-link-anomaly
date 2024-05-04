import mysql.connector
import os

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.host = os.getenv("DB_HOST")
            cls._instance.user = os.getenv("DB_USER")
            cls._instance.password = os.getenv("DB_PASSWORD")
            cls._instance.database = os.getenv("DB_DATABASE")
        return cls._instance

    def get_connection(self):
        # Selalu membuat koneksi baru setiap kali metode ini dipanggil
        connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        return connection
