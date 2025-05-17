"""
Asynchronous and concurrent processing utilities for task management.
This module demonstrates asynchronous programming with asyncio.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import concurrent.futures

from models import User, Task, TaskStatus
from app import db

# Configure logging
logger = logging.getLogger(__name__)


async def _process_task_metrics(user_id: int) -> Dict[str, Any]:
    """Process task metrics asynchronously.
    
    Args:
        user_id: User ID
        
    Returns:
        Dictionary with computed metrics
    """
    logger.info(f"Processing task metrics for user {user_id}")
    
    # Simulate time-consuming metrics processing
    await asyncio.sleep(0.5)
    
    # Get the user and their tasks
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}
    
    # Get active (non-deleted) tasks
    active_tasks = [task for task in user.tasks if not task.is_deleted]
    
    # Calculate basic metrics
    total_tasks = len(active_tasks)
    completed_tasks = sum(1 for task in active_tasks if task.status == TaskStatus.DONE)
    completion_rate = (completed_tasks / total_tasks) if total_tasks > 0 else 0
    
    # Calculate time-based metrics
    now = datetime.utcnow()
    overdue_tasks = sum(1 for task in active_tasks if task.is_overdue)
    
    # Calculate priority distribution
    priority_counts = {}
    for task in active_tasks:
        priority_name = task.priority.name
        priority_counts[priority_name] = priority_counts.get(priority_name, 0) + 1
    
    # Calculate completion trends over time
    completed_tasks_with_date = [
        task for task in active_tasks 
        if task.status == TaskStatus.DONE and task.completed_at
    ]
    
    # Group by completion date
    completion_trend = {}
    for task in completed_tasks_with_date:
        date_str = task.completed_at.strftime("%Y-%m-%d")
        completion_trend[date_str] = completion_trend.get(date_str, 0) + 1
    
    # Sort by date
    completion_trend_sorted = sorted(
        [{"date": k, "count": v} for k, v in completion_trend.items()],
        key=lambda x: x["date"]
    )
    
    # Combine all metrics
    metrics = {
        "user_id": user_id,
        "timestamp": now.isoformat(),
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_rate": completion_rate,
        "overdue_tasks": overdue_tasks,
        "priority_distribution": priority_counts,
        "completion_trend": completion_trend_sorted
    }
    
    logger.info(f"Metrics processing completed for user {user_id}")
    return metrics


def process_task_metrics_async(user_id: int) -> None:
    """Schedule task metrics processing asynchronously.
    
    Args:
        user_id: User ID
    """
    async def run_async():
        """Run the async task."""
        loop = asyncio.get_event_loop()
        metrics = await _process_task_metrics(user_id)
        logger.info(f"Task metrics generated: {json.dumps(metrics, default=str)}")
    
    # Schedule the coroutine to run soon
    asyncio.run(run_async())


async def _send_task_reminders(user_id: int) -> Dict[str, Any]:
    """Send reminders for upcoming tasks asynchronously.
    
    Args:
        user_id: User ID
        
    Returns:
        Dictionary with reminder results
    """
    logger.info(f"Sending task reminders for user {user_id}")
    
    # Simulate time for sending notifications
    await asyncio.sleep(1.0)
    
    # Get the user and their tasks
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}
    
    # Get active tasks due soon (not deleted, not completed, due within 24 hours)
    now = datetime.utcnow()
    tomorrow = now + timedelta(hours=24)
    
    due_soon_tasks = [
        task for task in user.tasks 
        if not task.is_deleted 
        and task.status != TaskStatus.DONE 
        and task.due_date 
        and now <= task.due_date <= tomorrow
    ]
    
    # Process reminders in parallel using task groups
    reminders_sent = []
    
    async def send_single_reminder(task):
        # Simulate sending a notification
        await asyncio.sleep(0.1)
        logger.info(f"Reminder sent for task {task.id}: {task.title}")
        return {
            "task_id": task.id,
            "title": task.title,
            "due_date": task.due_date.isoformat() if task.due_date else None
        }
    
    async with asyncio.TaskGroup() as tg:
        reminder_tasks = [
            tg.create_task(send_single_reminder(task))
            for task in due_soon_tasks
        ]
    
    # Collect results
    for task in reminder_tasks:
        reminders_sent.append(task.result())
    
    result = {
        "user_id": user_id,
        "timestamp": now.isoformat(),
        "reminders_sent": len(reminders_sent),
        "tasks": reminders_sent
    }
    
    logger.info(f"Task reminders sent for user {user_id}: {len(reminders_sent)} reminders")
    return result


def send_task_reminders_async(user_id: int) -> None:
    """Schedule sending task reminders asynchronously.
    
    Args:
        user_id: User ID
    """
    async def run_async():
        """Run the async task."""
        loop = asyncio.get_event_loop()
        result = await _send_task_reminders(user_id)
        logger.info(f"Task reminders sent: {json.dumps(result, default=str)}")
    
    # Schedule the coroutine to run soon
    asyncio.run(run_async())


async def _export_user_data(user_id: int) -> Dict[str, Any]:
    """Export all user data asynchronously.
    
    Args:
        user_id: User ID
        
    Returns:
        Dictionary with exported data
    """
    logger.info(f"Exporting data for user {user_id}")
    
    # Simulate time-consuming data export
    await asyncio.sleep(2.0)
    
    # Get the user and related data
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}
    
    # Process tasks and categories concurrently
    async def process_tasks():
        await asyncio.sleep(0.5)  # Simulate processing
        return [task.to_dict() for task in user.tasks]
    
    async def process_categories():
        await asyncio.sleep(0.5)  # Simulate processing
        return [category.to_dict() for category in user.categories]
    
    # Run processing concurrently
    tasks_future, categories_future = await asyncio.gather(
        process_tasks(),
        process_categories()
    )
    
    # Combine all data
    export_data = {
        "user": user.to_dict(),
        "tasks": tasks_future,
        "categories": categories_future,
        "export_date": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Data export completed for user {user_id}")
    return export_data


def export_user_data_async(user_id: int) -> None:
    """Schedule exporting user data asynchronously.
    
    Args:
        user_id: User ID
    """
    async def run_async():
        """Run the async task."""
        loop = asyncio.get_event_loop()
        result = await _export_user_data(user_id)
        
        # Simulating saving the export to a file
        export_id = f"export_{user_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        logger.info(f"User data exported: {export_id}")
    
    # Schedule the coroutine to run soon
    asyncio.run(run_async())


async def _process_concurrent_tasks(user_id: int) -> Dict[str, Any]:
    """Run multiple processing tasks concurrently.
    
    This function demonstrates use of asyncio.gather to run
    multiple coroutines concurrently.
    
    Args:
        user_id: User ID
        
    Returns:
        Dictionary with results of all concurrent operations
    """
    logger.info(f"Starting concurrent processing for user {user_id}")
    
    # Get results from all concurrent tasks
    metrics, reminders, _ = await asyncio.gather(
        _process_task_metrics(user_id),
        _send_task_reminders(user_id),
        _export_user_data(user_id)
    )
    
    logger.info(f"Completed concurrent processing for user {user_id}")
    
    return {
        "metrics": metrics,
        "reminders": reminders,
        "processed_at": datetime.utcnow().isoformat()
    }


def process_concurrent_tasks_async(user_id: int) -> None:
    """Schedule concurrent processing of multiple tasks.
    
    Args:
        user_id: User ID
    """
    async def run_async():
        """Run the async task."""
        loop = asyncio.get_event_loop()
        result = await _process_concurrent_tasks(user_id)
        logger.info("Concurrent processing completed")
    
    # Schedule the coroutine to run soon
    asyncio.run(run_async())
