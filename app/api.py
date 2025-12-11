from fastapi import APIRouter, HTTPException, status, Request
from schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.crud import TaskCRUD, DatabaseErrorException
from typing import List, Dict, Any
import logging
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/items",
    tags=["tasks"],
    responses={
        400: {"description": "Bad Request"},
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"}
    }
)

def handle_database_exception(e: DatabaseErrorException) -> Dict[str, Any]:
    """Maneja excepciones de base de datos"""
    error_response = {
        "error": True,
        "message": e.message,
        "error_code": e.error_code or "DATABASE_ERROR"
    }
    # depura en modo desarrollo
    import os
    if os.getenv("ENVIRONMENT") == "development":
        error_response["debug_info"] = str(e)
    return error_response

@router.get("/", response_model=List[TaskResponse], 
           summary="Get all tasks", description="Retrieve all tasks from the database")
async def get_all_items(request: Request):
    """Get all tasks"""
    try:
        tasks = TaskCRUD.get_all_tasks()
        return tasks
    except DatabaseErrorException as e:
        logger.error(f"Database error in get_all_items: {e.message}")
        raise HTTPException(
            status_code=e.status_code, detail=handle_database_exception(e) )
    except Exception as e:
        logger.error(f"Unexpected error in get_all_items: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={ "error": True,  "message": "An unexpected error occurred", "error_code": "INTERNAL_SERVER_ERROR"
            }
        )

@router.get("/{item_id}",  response_model=TaskResponse, summary="Get task by ID", description="Retrieve a specific task by its ID",
           responses={
               404: {"description": "Task not found"},
               400: {"description": "Invalid task ID"}
           })
async def get_item(item_id: int, request: Request):
    """Get a specific task by ID"""
    try:
        task = TaskCRUD.get_task_by_id(item_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={  "error": True,  "message": f"Task with id {item_id} not found", "error_code": "TASK_NOT_FOUND"  }
            )
        return task
    except DatabaseErrorException as e:
        logger.error(f"Database error in get_item: {e.message}")
        raise HTTPException( status_code=e.status_code, detail=handle_database_exception(e)
        )
    except HTTPException:
        raise   
    except Exception as e:
        logger.error(f"Unexpected error in get_item: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={ "error": True, "message": "An unexpected error occurred", "error_code": "INTERNAL_SERVER_ERROR"
            }
        )

@router.post("/", 
            response_model=TaskResponse, 
            status_code=status.HTTP_201_CREATED,
            summary="Create a new task",
            description="Create a new task with the data",
            responses={
                409: {"description": "Task already exists"},
                400: {"description": "Invalid task data"}
            })
async def create_item(task: TaskCreate, request: Request):
    """Create a new task"""
    try:
        created_task = TaskCRUD.create_task(task)
        return created_task
    except DatabaseErrorException as e:
        logger.error(f"Database error in create_item: {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail=handle_database_exception(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in create_item: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": True,
                "message": "An unexpected error occurred while creating task",
                "error_code": "INTERNAL_SERVER_ERROR"
            }
        )

@router.put("/{item_id}", 
           response_model=TaskResponse,
           summary="Update a task",
           description="Update an existing task with new data",
           responses={
               404: {"description": "Task not found"},
               400: {"description": "Invalid update data"}
           })
async def update_item(item_id: int, task_update: TaskUpdate, request: Request):
    """Update an existing task with"""
    try:
        updated_task = TaskCRUD.update_task(item_id, task_update)
        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": True,
                    "message": f"Task with id {item_id} not found",
                    "error_code": "TASK_NOT_FOUND"
                }
            )
        return updated_task
    except DatabaseErrorException as e:
        logger.error(f"Database error in update_item: {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail=handle_database_exception(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_item: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": True,
                "message": "An unexpected error occurred while updating task",
                "error_code": "INTERNAL_SERVER_ERROR"
            }
        )

@router.delete("/{item_id}", 
              status_code=status.HTTP_204_NO_CONTENT,
              summary="Delete a task",
              description="Delete a task by its ID",
              responses={
                  404: {"description": "Task not found"},
                  400: {"description": "Invalid task ID"}
              })
async def delete_item(item_id: int, request: Request):
    """Delete a task with"""
    try:
        deleted = TaskCRUD.delete_task(item_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": True,
                    "message": f"Task with id {item_id} not found",
                    "error_code": "TASK_NOT_FOUND"
                }
            )
        return None
        
    except DatabaseErrorException as e:
        logger.error(f"Database error in delete_item: {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail=handle_database_exception(e)
        )
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error in delete_item: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": True,
                "message": "An unexpected error occurred while deleting task",
                "error_code": "INTERNAL_SERVER_ERROR"
            }
        )

@router.get("/health/check", 
           summary="Health check",
           description="Check the health status of the API and database connection")
async def health_check():
    """Health check endpoint with database connectivity test"""
    try:
        # Intentar obtener una conexión a la base de datos
        from database.connection import get_db_connection
        connection = get_db_connection()
        
        # Ejecutar una consulta simple para verificar la conectividad
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        
        if result and result[0] == 1:
            return {
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "unhealthy",
                "database": "query_failed",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }