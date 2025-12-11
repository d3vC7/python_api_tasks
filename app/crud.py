from database.connection import get_db_connection, DatabaseErrorException
from schemas.task import TaskCreate, TaskUpdate
from typing import List, Optional, Dict, Any
from decimal import Decimal, InvalidOperation
import mysql.connector
from mysql.connector import Error, IntegrityError, DataError
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TaskCRUD:
    
    @staticmethod
    def get_all_tasks() -> List[Dict[str, Any]]:
        """Get all tasks"""
        connection = None
        cursor = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM tasks ORDER BY created_at ASC"
            cursor.execute(query)
            tasks = cursor.fetchall()
            logger.info(f"Retrieved {len(tasks)} tasks successfully")
            return tasks
        except DatabaseErrorException as e:
            raise e
        except Error as e:
            logger.error(f"Database error fetching tasks: {e}")
            raise DatabaseErrorException(
                message="Failed to fetch tasks from database",
                status_code=500,
                error_code="FETCH_TASKS_ERROR"
            )
        except Exception as e:
            logger.error(f"Unexpected error fetching tasks: {e}")
            raise DatabaseErrorException(
                message="An unexpected error occurred",
                status_code=500,
                error_code="UNEXPECTED_FETCH_ERROR"
            )
        finally:
            if cursor:
                cursor.close()
    
    @staticmethod
    def get_task_by_id(task_id: int) -> Optional[Dict[str, Any]]:
        """Get a task by ID"""
        connection = None
        cursor = None
        try:
            if not isinstance(task_id, int) or task_id <= 0:
                raise ValueError("Invalid task ID")
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM tasks WHERE id = %s"
            cursor.execute(query, (task_id,))
            task = cursor.fetchone()
            if task:
                logger.info(f"Retrieved task ID {task_id} successfully")
            else:
                logger.warning(f"Task ID {task_id} not found")
            return task
        except ValueError as e:
            logger.warning(f"Invalid input for task ID: {e}")
            raise DatabaseErrorException(
                message=str(e),
                status_code=400,
                error_code="INVALID_INPUT"
            )
        except DatabaseErrorException as e:
            raise e
        except Error as e:
            logger.error(f"Database error fetching task {task_id}: {e}")
            raise DatabaseErrorException(
                message=f"Failed to fetch task with ID {task_id}",
                status_code=500,
                error_code="FETCH_TASK_ERROR"
            )
        except Exception as e:
            logger.error(f"Unexpected error fetching task {task_id}: {e}")
            raise DatabaseErrorException(
                message="An unexpected error occurred while fetching task",
                status_code=500,
                error_code="UNEXPECTED_TASK_ERROR"
            )
        finally:
            if cursor:
                cursor.close()
    
    @staticmethod
    def create_task(task: TaskCreate) -> Dict[str, Any]:
        """Crate a mew task"""
        connection = None
        cursor = None
        try:
            TaskCRUD._validate_task_data(task)
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            query = """
            INSERT INTO tasks (name, description, price)
            VALUES (%s, %s, %s)
            """
            price_value = float(task.price)
            cursor.execute(query, (task.name, task.description, price_value))
            connection.commit()
            task_id = cursor.lastrowid
            query = "SELECT * FROM tasks WHERE id = %s"
            cursor.execute(query, (task_id,))
            created_task = cursor.fetchone()
            if created_task:
                logger.info(f"Created task ID {task_id} successfully")
            else:
                logger.error(f"Failed to retrieve created task ID {task_id}")
                raise DatabaseErrorException(
                    message="Failed to retrieve created task",
                    status_code=500,
                    error_code="TASK_RETRIEVAL_ERROR"
                )
            return created_task
        except InvalidOperation as e:
            logger.error(f"Invalid price value: {e}")
            raise DatabaseErrorException(
                message="Invalid price format",
                status_code=400,
                error_code="INVALID_PRICE_FORMAT"
            )
        except IntegrityError as e:
            if connection:
                connection.rollback()
            logger.error(f"Integrity error creating task: {e}")
            if "Duplicate entry" in str(e):
                raise DatabaseErrorException(
                    message="A task with similar data already exists",
                    status_code=409,
                    error_code="DUPLICATE_TASK"
                )
            else:
                raise DatabaseErrorException(
                    message="Database integrity constraint violated",
                    status_code=400,
                    error_code="INTEGRITY_ERROR"
                )
        except DataError as e:
            if connection:
                connection.rollback()
            logger.error(f"Data error creating task: {e}")
            raise DatabaseErrorException(
                message="Invalid data provided. Please check field lengths and types.",
                status_code=400,
                error_code="INVALID_DATA"
            )
        except DatabaseErrorException as e:
            if connection:
                connection.rollback()
            raise e
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Database error creating task: {e}")
            raise DatabaseErrorException(
                message="Failed to create task in database",
                status_code=500,
                error_code="CREATE_TASK_ERROR"
            )
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Unexpected error creating task: {e}")
            raise DatabaseErrorException(
                message="An unexpected error occurred while creating task",
                status_code=500,
                error_code="UNEXPECTED_CREATE_ERROR"
            )
        finally:
            if cursor:
                cursor.close()
    
    @staticmethod
    def update_task(task_id: int, task_update: TaskUpdate) -> Optional[Dict[str, Any]]:
        """Update an existing task"""
        connection = None
        cursor = None
        try:
            if not isinstance(task_id, int) or task_id <= 0:
                raise ValueError("Invalid task ID")
            existing_task = TaskCRUD.get_task_by_id(task_id)
            if not existing_task:
                return None
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            update_fields = []
            values = []
            if task_update.name is not None:
                if not task_update.name.strip():
                    raise ValueError("Task name cannot be empty")
                update_fields.append("name = %s")
                values.append(task_update.name.strip())
            if task_update.description is not None:
                update_fields.append("description = %s")
                values.append(task_update.description.strip() if task_update.description else None)
            if task_update.price is not None:
                try:
                    price_value = float(task_update.price)
                    if price_value <= 0:
                        raise ValueError("Price must be greater than 0")
                    update_fields.append("price = %s")
                    values.append(price_value)
                except (ValueError, InvalidOperation) as e:
                    raise ValueError(f"Invalid price value: {e}")
            if not update_fields:
                return existing_task
            update_query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = %s"
            values.append(task_id)
            cursor.execute(update_query, tuple(values))
            connection.commit()
            rows_affected = cursor.rowcount
            if rows_affected == 0:
                logger.warning(f"No rows affected when updating task ID {task_id}")
            updated_task = TaskCRUD.get_task_by_id(task_id)
            logger.info(f"Updated task ID {task_id} successfully")
            return updated_task
        except ValueError as e:
            if connection:
                connection.rollback()
            logger.warning(f"Invalid input for task update: {e}")
            raise DatabaseErrorException(
                message=str(e),
                status_code=400,
                error_code="INVALID_UPDATE_INPUT"
            )
        except IntegrityError as e:
            if connection:
                connection.rollback()
            logger.error(f"Integrity error updating task {task_id}: {e}")
            raise DatabaseErrorException(
                message="Database integrity constraint violated",
                status_code=400,
                error_code="UPDATE_INTEGRITY_ERROR"
            )
        except DatabaseErrorException as e:
            if connection:
                connection.rollback()
            raise e
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Database error updating task {task_id}: {e}")
            raise DatabaseErrorException(
                message=f"Failed to update task with ID {task_id}",
                status_code=500,
                error_code="UPDATE_TASK_ERROR"
            )
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Unexpected error updating task {task_id}: {e}")
            raise DatabaseErrorException(
                message="An unexpected error occurred while updating task",
                status_code=500,
                error_code="UNEXPECTED_UPDATE_ERROR"
            )
        finally:
            if cursor:
                cursor.close()
    
    @staticmethod
    def delete_task(task_id: int) -> bool:
        """Delete a taskk"""
        connection = None
        cursor = None
        try:
            if not isinstance(task_id, int) or task_id <= 0:
                raise ValueError("Invalid task ID")
            existing_task = TaskCRUD.get_task_by_id(task_id)
            if not existing_task:
                return False
            connection = get_db_connection()
            cursor = connection.cursor()
            query = "DELETE FROM tasks WHERE id = %s"
            cursor.execute(query, (task_id,))
            connection.commit()
            rows_affected = cursor.rowcount
            deleted = rows_affected > 0
            if deleted:
                logger.info(f"Deleted task ID {task_id} successfully")
            else:
                logger.warning(f"No task deleted for ID {task_id}")
            return deleted
        except ValueError as e:
            if connection:
                connection.rollback()
            logger.warning(f"Invalid input for task deletion: {e}")
            raise DatabaseErrorException(
                message=str(e),
                status_code=400,
                error_code="INVALID_DELETE_INPUT"
            )
        except DatabaseErrorException as e:
            if connection:
                connection.rollback()
            raise e
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Database error deleting task {task_id}: {e}")
            raise DatabaseErrorException(
                message=f"Failed to delete task with ID {task_id}",
                status_code=500,
                error_code="DELETE_TASK_ERROR"
            )
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Unexpected error deleting task {task_id}: {e}")
            raise DatabaseErrorException(
                message="An unexpected error occurred while deleting task",
                status_code=500,
                error_code="UNEXPECTED_DELETE_ERROR"
            )
        finally:
            if cursor:
                cursor.close()
    
    @staticmethod
    def _validate_task_data(task_data) -> None:
        """Validate data task"""
        if hasattr(task_data, 'name'):
            if not task_data.name or not task_data.name.strip():
                raise ValueError("Task name is required and cannot be empty")
            if len(task_data.name.strip()) > 255:
                raise ValueError("Task name cannot exceed 255 characters")
        if hasattr(task_data, 'description') and task_data.description:
            if len(task_data.description) > 1000:
                raise ValueError("Description cannot exceed 1000 characters")
        if hasattr(task_data, 'price'):
            try:
                price = float(task_data.price)
                if price <= 0:
                    raise ValueError("Price must be greater than 0")
                if price > 99999999.99:  # Límite basado en DECIMAL(10,2)
                    raise ValueError("Price exceeds maximum allowed value")
            except (ValueError, TypeError, InvalidOperation):
                raise ValueError("Invalid price format")