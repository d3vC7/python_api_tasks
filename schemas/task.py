from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal

class TaskBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Task name")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    price: Decimal = Field(..., gt=0, description="Task price")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[Decimal] = Field(None, gt=0)

class TaskInDB(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TaskResponse(TaskInDB):
    pass