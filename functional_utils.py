"""
Functional programming utilities for task management.
This module demonstrates functional programming paradigms with pure functions,
higher-order functions, and functional composition.
"""

from typing import List, Dict, Any, Callable, Optional, TypeVar, Union
from datetime import datetime, timedelta
from functools import reduce, partial
from itertools import groupby

from models import Task, Category, TaskStatus, TaskPriority

T = TypeVar('T')


# ===== Pure Functions =====

def filter_tasks(tasks: List[Task], predicate: Callable[[Task], bool]) -> List[Task]:
    """Filter tasks based on a predicate function.
    
    Args:
        tasks: List of tasks to filter
        predicate: Function that returns True for tasks to keep
        
    Returns:
        Filtered list of tasks
    """
    return list(filter(predicate, tasks))


def sort_tasks(tasks: List[Task], sort_by: str = 'due_date', sort_order: str = 'asc') -> List[Task]:
    """Sort tasks based on a field and order.
    
    Args:
        tasks: List of tasks to sort
        sort_by: Field to sort by (e.g., 'due_date', 'priority', 'title')
        sort_order: Sort order ('asc' or 'desc')
        
    Returns:
        Sorted list of tasks
    """
    if not tasks:
        return []
    
    # Define key functions for different sort fields
    key_funcs = {
        'title': lambda t: t.title.lower(),
        'due_date': lambda t: t.due_date or datetime.max,
        'priority': lambda t: t.priority.value,
        'status': lambda t: t.status.value,
        'created_at': lambda t: t.created_at,
        'category': lambda t: t.category.name.lower() if t.category else 'zzzz'
    }
    
    # Get the key function or default to title
    key_func = key_funcs.get(sort_by, key_funcs['title'])
    
    # Sort the tasks
    sorted_tasks = sorted(tasks, key=key_func, reverse=(sort_order.lower() == 'desc'))
    return sorted_tasks


def count_tasks_by_status(tasks: List[Task]) -> Dict[str, int]:
    """Count tasks by status.
    
    Args:
        tasks: List of tasks
        
    Returns:
        Dictionary mapping status names to counts
    """
    result = {status.name: 0 for status in TaskStatus}
    
    for task in tasks:
        result[task.status.name] += 1
    
    return result


def count_tasks_by_priority(tasks: List[Task]) -> Dict[str, int]:
    """Count tasks by priority.
    
    Args:
        tasks: List of tasks
        
    Returns:
        Dictionary mapping priority names to counts
    """
    result = {priority.name: 0 for priority in TaskPriority}
    
    for task in tasks:
        result[task.priority.name] += 1
    
    return result


def count_tasks_by_category(tasks: List[Task]) -> Dict[int, int]:
    """Count tasks by category ID.
    
    Args:
        tasks: List of tasks
        
    Returns:
        Dictionary mapping category IDs to counts
    """
    return reduce(
        lambda acc, task: {
            **acc, 
            task.category_id: acc.get(task.category_id, 0) + 1
        },
        tasks,
        {}
    )


def group_tasks_by(tasks: List[Task], key_func: Callable[[Task], Any]) -> Dict[Any, List[Task]]:
    """Group tasks by a key function.
    
    Args:
        tasks: List of tasks to group
        key_func: Function to extract the grouping key
        
    Returns:
        Dictionary mapping keys to lists of tasks
    """
    sorted_tasks = sorted(tasks, key=key_func)
    return {k: list(g) for k, g in groupby(sorted_tasks, key=key_func)}


def map_tasks(tasks: List[Task], transform_func: Callable[[Task], T]) -> List[T]:
    """Apply a transformation function to each task.
    
    Args:
        tasks: List of tasks
        transform_func: Function to transform each task
        
    Returns:
        List of transformed tasks
    """
    return list(map(transform_func, tasks))


def get_completion_rate(tasks: List[Task]) -> float:
    """Calculate task completion rate.
    
    Args:
        tasks: List of tasks
        
    Returns:
        Completion rate as a float (0-1)
    """
    if not tasks:
        return 0.0
    
    completed = sum(1 for task in tasks if task.status == TaskStatus.DONE)
    return completed / len(tasks)


def get_overdue_tasks(user_id: int) -> List[Task]:
    """Get overdue tasks for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        List of overdue tasks
    """
    from app import db
    
    # Query for tasks that are:
    # 1. Not deleted
    # 2. Not completed
    # 3. Have a due date in the past
    now = datetime.utcnow()
    
    overdue_tasks = db.session.query(Task).filter(
        Task.user_id == user_id,
        Task.is_deleted == False,
        Task.status != TaskStatus.DONE,
        Task.due_date.isnot(None),
        Task.due_date < now
    ).all()
    
    return overdue_tasks


def get_task_stats(tasks: List[Task]) -> Dict[str, Any]:
    """Get comprehensive task statistics.
    
    Args:
        tasks: List of tasks
        
    Returns:
        Dictionary with task statistics
    """
    if not tasks:
        return {
            'total': 0,
            'completed': 0,
            'pending': 0,
            'overdue': 0,
            'completion_rate': 0,
            'by_status': {status.name: 0 for status in TaskStatus},
            'by_priority': {priority.name: 0 for priority in TaskPriority}
        }
    
    # Filter non-deleted tasks
    active_tasks = filter_tasks(tasks, lambda t: not t.is_deleted)
    
    # Count by status
    by_status = count_tasks_by_status(active_tasks)
    
    # Count by priority
    by_priority = count_tasks_by_priority(active_tasks)
    
    # Count completed, pending, and overdue
    completed = by_status.get(TaskStatus.DONE.name, 0)
    total = len(active_tasks)
    pending = total - completed
    overdue = len(filter_tasks(active_tasks, lambda t: t.is_overdue))
    
    # Calculate completion rate
    completion_rate = (completed / total) if total > 0 else 0
    
    return {
        'total': total,
        'completed': completed,
        'pending': pending,
        'overdue': overdue,
        'completion_rate': completion_rate,
        'by_status': by_status,
        'by_priority': by_priority
    }


def get_category_stats(categories: List[Category]) -> Dict[str, Any]:
    """Get comprehensive category statistics.
    
    Args:
        categories: List of categories
        
    Returns:
        Dictionary with category statistics
    """
    if not categories:
        return {
            'total': 0,
            'categories': []
        }
    
    # Filter non-deleted categories
    active_categories = filter(lambda c: not c.is_deleted, categories)
    
    # Transform to dictionary
    categories_data = []
    for category in active_categories:
        # Filter non-deleted tasks
        active_tasks = filter_tasks(category.tasks, lambda t: not t.is_deleted)
        
        # Count tasks by status
        by_status = count_tasks_by_status(active_tasks)
        
        # Calculate completion rate
        total_tasks = len(active_tasks)
        completed_tasks = by_status.get(TaskStatus.DONE.name, 0)
        completion_rate = (completed_tasks / total_tasks) if total_tasks > 0 else 0
        
        categories_data.append({
            'id': category.id,
            'name': category.name,
            'color': category.color,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': completion_rate
        })
    
    return {
        'total': len(categories_data),
        'categories': categories_data
    }


def compose(*functions):
    """Function composition.
    
    Composes functions from right to left.
    compose(f, g, h)(x) is equivalent to f(g(h(x)))
    
    Args:
        *functions: Functions to compose
        
    Returns:
        Composed function
    """
    if not functions:
        return lambda x: x
    
    if len(functions) == 1:
        return functions[0]
    
    return reduce(lambda f, g: lambda x: f(g(x)), functions)


def pipe(value, *functions):
    """Function pipeline.
    
    Pipes a value through a series of functions from left to right.
    pipe(x, f, g, h) is equivalent to h(g(f(x)))
    
    Args:
        value: Initial value
        *functions: Functions to apply
        
    Returns:
        Result of applying functions to value
    """
    return reduce(lambda acc, fn: fn(acc), functions, value)


# ==== Higher-order function applications ====

# Predefined filters
is_completed = lambda task: task.status == TaskStatus.DONE
is_pending = lambda task: task.status != TaskStatus.DONE
is_high_priority = lambda task: task.priority in (TaskPriority.HIGH, TaskPriority.URGENT)
is_due_this_week = lambda task: (
    task.due_date and 
    datetime.utcnow().date() <= task.due_date.date() <= 
    (datetime.utcnow() + timedelta(days=7)).date()
)

# Partial applications
get_completed_tasks = partial(filter_tasks, predicate=is_completed)
get_pending_tasks = partial(filter_tasks, predicate=is_pending)
get_high_priority_tasks = partial(filter_tasks, predicate=is_high_priority)
get_this_week_tasks = partial(filter_tasks, predicate=is_due_this_week)
