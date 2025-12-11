import mysql.connector
from mysql.connector import Error, DatabaseError, InterfaceError, PoolError
import os
import time
from typing import Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseErrorException(Exception):
    """Exception for errors in dtabase"""
    def __init__(self, message: str, status_code: int = 500, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

class DatabaseConnection:
    _instance = None
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance
    
    def _initialize_connection(self, retry_count: int = 0):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'mysql'),
                port=os.getenv('DB_PORT', '3306'),
                database=os.getenv('DB_NAME', 'taskdb'),
                user=os.getenv('DB_USER', 'taskuser'),
                password=os.getenv('DB_PASSWORD', 'taskpassword'),
                connection_timeout=30,
                pool_size=5,
                buffered=True,
                autocommit=False 
            )
            logger.info("Database connection established successfully")
        except InterfaceError as e:
            logger.error(f"Interface error connecting to MySQL: {e}")
            if retry_count < self.MAX_RETRIES:
                logger.info(f"Retrying connection in {self.RETRY_DELAY} seconds... (Attempt {retry_count + 1}/{self.MAX_RETRIES})")
                time.sleep(self.RETRY_DELAY)
                return self._initialize_connection(retry_count + 1)
            raise DatabaseErrorException(
                message="Database service unavailable. Please try again later.",
                status_code=503,
                error_code="DB_CONNECTION_FAILED"
            )
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            error_msg = str(e)
            if "Access denied" in error_msg:
                raise DatabaseErrorException(
                    message="Database authentication failed",
                    status_code=401,
                    error_code="DB_AUTH_FAILED"
                )
            elif "Unknown database" in error_msg:
                raise DatabaseErrorException(
                    message="Database not found",
                    status_code=404,
                    error_code="DB_NOT_FOUND"
                )
            else:
                raise DatabaseErrorException(
                    message=f"Database connection error: {error_msg}",
                    status_code=500,
                    error_code="DB_CONNECTION_ERROR"
                )
    
    def get_connection(self):
        try:
            if self.connection and self.connection.is_connected():
                self.connection.ping(reconnect=True, attempts=1, delay=0)
                return self.connection
            else:
                logger.warning("Connection lost, reinitializing...")
                self._initialize_connection()
                return self.connection
        except Error as e:
            logger.error(f"Error getting database connection: {e}")
            raise DatabaseErrorException(
                message="Unable to establish database connection",
                status_code=503,
                error_code="DB_CONNECTION_LOST"
            )
    
    def execute_transaction(self, operations):
        """Ejecuta múltiples operaciones en una transacción"""
        connection = self.get_connection()
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            connection.start_transaction()
            results = []
            for operation in operations:
                query, params = operation
                cursor.execute(query, params)
                if cursor.description:  # Si hay resultados
                    results.append(cursor.fetchall())
                else:
                    results.append(cursor.rowcount)
            connection.commit()
            return results
        except DatabaseError as e:
            if connection:
                connection.rollback()
            logger.error(f"Database transaction error: {e}")
            raise DatabaseErrorException(
                message=f"Transaction failed: {str(e)}",
                status_code=500,
                error_code="TRANSACTION_FAILED"
            )
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Error during transaction: {e}")
            raise DatabaseErrorException(
                message="An error occurred during database operation",
                status_code=500,
                error_code="DB_OPERATION_ERROR"
            )
        finally:
            if cursor:
                cursor.close()
    
    def close_connection(self):
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close()
                logger.info("Database connection closed successfully")
        except Error as e:
            logger.error(f"Error closing database connection: {e}")

def get_db_connection():
    """Get a conection to the database"""
    try:
        db = DatabaseConnection()
        return db.get_connection()
    except DatabaseErrorException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error getting database connection: {e}")
        raise DatabaseErrorException(
            message="Unexpected database error",
            status_code=500,
            error_code="UNEXPECTED_DB_ERROR"
        )