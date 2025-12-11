import mysql.connector
from mysql.connector import Error
import os
import time
from typing import Optional
import logging

class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance
    
    def _initialize_connection(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'mysql'),
                port=os.getenv('DB_PORT', '3306'),
                database=os.getenv('DB_NAME', 'taskdb'),
                user=os.getenv('DB_USER', 'taskuser'),
                password=os.getenv('DB_PASSWORD', 'taskpassword')
            )
            print("Database connection established successfully")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            self.connection = None
    
    def get_connection(self):
        if self.connection and self.connection.is_connected():
            return self.connection
        else:
            self._initialize_connection()
            return self.connection
    
    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

def get_db_connection():
    db = DatabaseConnection()
    return db.get_connection()