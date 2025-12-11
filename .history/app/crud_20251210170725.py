from database.connection import get_db_connection
from schemas.task import TaskCreate, TaskUpdate
from typing import List, Optional
from decimal import Decimal

class TaskCRUD:
    
    @staticmethod
    def get_all_tasks() -> List[dict]:
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM tasks ORDER BY created_at ASC"
            cursor.execute(query)
            tasks = cursor.fetchall()
            cursor.close()
            return tasks
        except Exception as e:
                return {"status": "error", "message": f"get_all_tasks. An unexpected error occurred: {e}"}

    @staticmethod
    def get_task_by_id(task_id: int) -> Optional[dict]:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM tasks WHERE id = %s"
        cursor.execute(query, (task_id,))
        task = cursor.fetchone()
        
        cursor.close()
        return task
    
    @staticmethod
    def create_task(task: TaskCreate) -> dict:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        INSERT INTO tasks (name, description, price)
        VALUES (%s, %s, %s)
        """
        values = (task.name, task.description, float(task.price))
        
        cursor.execute(query, values)
        connection.commit()
        
        task_id = cursor.lastrowid
        
        # Get the created task
        query = "SELECT * FROM tasks WHERE id = %s"
        cursor.execute(query, (task_id,))
        created_task = cursor.fetchone()
        
        cursor.close()
        return created_task
    
    @staticmethod
    def update_task(task_id: int, task_update: TaskUpdate) -> Optional[dict]:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # First, check if task exists
        check_query = "SELECT id FROM tasks WHERE id = %s"
        cursor.execute(check_query, (task_id,))
        if not cursor.fetchone():
            cursor.close()
            return None
        
        # Build update query dynamically based on provided fields
        update_fields = []
        values = []
        
        if task_update.name is not None:
            update_fields.append("name = %s")
            values.append(task_update.name)
        
        if task_update.description is not None:
            update_fields.append("description = %s")
            values.append(task_update.description)
        
        if task_update.price is not None:
            update_fields.append("price = %s")
            values.append(float(task_update.price))
        
        if not update_fields:
            # No fields to update
            cursor.close()
            return TaskCRUD.get_task_by_id(task_id)
        
        update_query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = %s"
        values.append(task_id)
        
        cursor.execute(update_query, tuple(values))
        connection.commit()
        
        # Get updated task
        updated_task = TaskCRUD.get_task_by_id(task_id)
        
        cursor.close()
        return updated_task
    
    @staticmethod
    def delete_task(task_id: int) -> bool:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = "DELETE FROM tasks WHERE id = %s"
        cursor.execute(query, (task_id,))
        connection.commit()
        
        rows_affected = cursor.rowcount
        cursor.close()
        
        return rows_affected > 0