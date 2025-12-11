from fastapi import APIRouter, HTTPException, status
from schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.crud import TaskCRUD
from typing import List

router = APIRouter()

@router.get("/items", response_model=List[TaskResponse])
async def get_all_items():
    """Get all tasks"""
    tasks = TaskCRUD.get_all_tasks()
    return tasks

@router.get("/items/{item_id}", response_model=TaskResponse)
async def get_item(item_id: int):
    """Get a task by ID"""
    task = TaskCRUD.get_task_by_id(item_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {item_id} not found"
        )
    return task

@router.post("/items", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_item(task: TaskCreate):
    """Create a new task"""
    created_task = TaskCRUD.create_task(task)
    return created_task

@router.put("/items/{item_id}", response_model=TaskResponse)
async def update_item(item_id: int, task_update: TaskUpdate):
    """Update an existing task"""
    updated_task = TaskCRUD.update_task(item_id, task_update)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {item_id} not found"
        )
    return updated_task

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    """Delete a task"""
    deleted = TaskCRUD.delete_task(item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {item_id} not found"
        )
    return None