"""
Роутер для управления планировщиком задач.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ..database import get_database
from ..auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

class TaskCreate(BaseModel):
    """Модель для создания задачи."""
    name: str
    description: Optional[str] = None
    schedule: str  # Cron expression
    enabled: bool = True
    session_name: str
    parameters: Optional[Dict[str, Any]] = None

class TaskUpdate(BaseModel):
    """Модель для обновления задачи."""
    name: Optional[str] = None
    description: Optional[str] = None
    schedule: Optional[str] = None
    enabled: Optional[bool] = None
    parameters: Optional[Dict[str, Any]] = None

class TaskResponse(BaseModel):
    """Модель для ответа с задачей."""
    id: str
    name: str
    description: Optional[str]
    schedule: str
    enabled: bool
    session_name: str
    parameters: Dict[str, Any]
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    status: str
    created_at: datetime
    updated_at: datetime

class TaskExecution(BaseModel):
    """Модель для выполнения задачи."""
    task_id: str
    started_at: datetime
    finished_at: Optional[datetime]
    status: str
    result: Optional[Dict[str, Any]]
    error: Optional[str]

@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    enabled: Optional[bool] = Query(None),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Получает список задач."""
    try:
        tasks_collection = db.get_collection("tasks")
        
        # Строим фильтр
        filter_dict = {}
        if enabled is not None:
            filter_dict["enabled"] = enabled
        
        # Получаем задачи
        tasks = await tasks_collection.find(
            filter_dict,
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
        
        return [
            TaskResponse(
                id=task["id"],
                name=task["name"],
                description=task.get("description"),
                schedule=task["schedule"],
                enabled=task["enabled"],
                session_name=task["session_name"],
                parameters=task.get("parameters", {}),
                last_run=task.get("last_run"),
                next_run=task.get("next_run"),
                status=task["status"],
                created_at=task["created_at"],
                updated_at=task["updated_at"]
            )
            for task in tasks
        ]
        
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail="Error getting tasks")

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Получает задачу по ID."""
    try:
        tasks_collection = db.get_collection("tasks")
        task = await tasks_collection.find_one({"id": task_id}, {"_id": 0})
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskResponse(**task)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Error getting task")

@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Создает новую задачу."""
    try:
        tasks_collection = db.get_collection("tasks")
        
        # Генерируем ID задачи
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(task_data.name) % 10000}"
        
        # Создаем задачу
        task = {
            "id": task_id,
            "name": task_data.name,
            "description": task_data.description,
            "schedule": task_data.schedule,
            "enabled": task_data.enabled,
            "session_name": task_data.session_name,
            "parameters": task_data.parameters or {},
            "last_run": None,
            "next_run": None,
            "status": "created",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Сохраняем в базу данных
        await tasks_collection.insert_one(task)
        
        # Здесь должна быть логика регистрации задачи в Celery Beat
        # register_task_in_scheduler(task)
        
        return TaskResponse(**task)
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail="Error creating task")

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Обновляет задачу."""
    try:
        tasks_collection = db.get_collection("tasks")
        
        # Проверяем, существует ли задача
        existing_task = await tasks_collection.find_one({"id": task_id}, {"_id": 0})
        if not existing_task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Обновляем только переданные поля
        update_data = {"updated_at": datetime.now()}
        if task_data.name is not None:
            update_data["name"] = task_data.name
        if task_data.description is not None:
            update_data["description"] = task_data.description
        if task_data.schedule is not None:
            update_data["schedule"] = task_data.schedule
        if task_data.enabled is not None:
            update_data["enabled"] = task_data.enabled
        if task_data.parameters is not None:
            update_data["parameters"] = task_data.parameters
        
        # Сохраняем изменения
        await tasks_collection.update_one(
            {"id": task_id},
            {"$set": update_data}
        )
        
        # Получаем обновленную задачу
        updated_task = await tasks_collection.find_one({"id": task_id}, {"_id": 0})
        
        # Здесь должна быть логика обновления задачи в Celery Beat
        # update_task_in_scheduler(updated_task)
        
        return TaskResponse(**updated_task)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating task")

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Удаляет задачу."""
    try:
        tasks_collection = db.get_collection("tasks")
        
        # Проверяем, существует ли задача
        existing_task = await tasks_collection.find_one({"id": task_id}, {"_id": 0})
        if not existing_task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Удаляем задачу
        await tasks_collection.delete_one({"id": task_id})
        
        # Здесь должна быть логика удаления задачи из Celery Beat
        # remove_task_from_scheduler(task_id)
        
        return {"message": "Task deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting task")

@router.post("/tasks/{task_id}/run")
async def run_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Запускает задачу немедленно."""
    try:
        tasks_collection = db.get_collection("tasks")
        
        # Проверяем, существует ли задача
        existing_task = await tasks_collection.find_one({"id": task_id}, {"_id": 0})
        if not existing_task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Обновляем статус
        await tasks_collection.update_one(
            {"id": task_id},
            {
                "$set": {
                    "status": "running",
                    "last_run": datetime.now(),
                    "updated_at": datetime.now()
                }
            }
        )
        
        # Здесь должна быть логика запуска задачи через Celery
        # run_task_now.delay(task_id)
        
        return {"message": "Task queued for execution"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Error running task")

@router.get("/executions", response_model=List[TaskExecution])
async def get_task_executions(
    task_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Получает историю выполнения задач."""
    try:
        executions_collection = db.get_collection("task_executions")
        
        # Строим фильтр
        filter_dict = {}
        if task_id:
            filter_dict["task_id"] = task_id
        
        # Получаем выполнения
        executions = await executions_collection.find(
            filter_dict,
            {"_id": 0}
        ).sort("started_at", -1).skip(skip).limit(limit).to_list(length=limit)
        
        return [
            TaskExecution(
                task_id=execution["task_id"],
                started_at=execution["started_at"],
                finished_at=execution.get("finished_at"),
                status=execution["status"],
                result=execution.get("result"),
                error=execution.get("error")
            )
            for execution in executions
        ]
        
    except Exception as e:
        logger.error(f"Error getting task executions: {e}")
        raise HTTPException(status_code=500, detail="Error getting task executions")

@router.get("/status")
async def get_scheduler_status(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Получает статус планировщика."""
    try:
        tasks_collection = db.get_collection("tasks")
        executions_collection = db.get_collection("task_executions")
        
        # Статистика задач
        total_tasks = await tasks_collection.count_documents({})
        enabled_tasks = await tasks_collection.count_documents({"enabled": True})
        running_tasks = await tasks_collection.count_documents({"status": "running"})
        
        # Статистика выполнений за последние 24 часа
        yesterday = datetime.now() - timedelta(days=1)
        executions_today = await executions_collection.count_documents({
            "started_at": {"$gte": yesterday}
        })
        successful_executions = await executions_collection.count_documents({
            "started_at": {"$gte": yesterday},
            "status": "success"
        })
        failed_executions = await executions_collection.count_documents({
            "started_at": {"$gte": yesterday},
            "status": "error"
        })
        
        return {
            "tasks": {
                "total": total_tasks,
                "enabled": enabled_tasks,
                "running": running_tasks
            },
            "executions": {
                "today": executions_today,
                "successful": successful_executions,
                "failed": failed_executions
            },
            "scheduler": {
                "status": "running",  # Здесь должна быть проверка статуса Celery Beat
                "last_check": datetime.now()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        raise HTTPException(status_code=500, detail="Error getting scheduler status")
