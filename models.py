import enum
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from app import db

# ===== OOP: Base Classes =====

class TimeStampMixin:
    """Base mixin for tracking creation and update times."""
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SoftDeleteMixin:
    """Base mixin for soft deletes."""
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    
    def soft_delete(self):
        """Mark entity as deleted without removing from database."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()


class TaskPriority(enum.Enum):
    """Enum for task priorities."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class TaskStatus(enum.Enum):
    """Enum for task statuses."""
    TODO = 1
    IN_PROGRESS = 2
    REVIEW = 3
    DONE = 4
    ARCHIVED = 5


# ===== OOP: Entity Classes =====

class User(UserMixin, TimeStampMixin, db.Model):
    """User entity class."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    first_name = Column(String(64), nullable=True)
    last_name = Column(String(64), nullable=True)
    
    # Relationships
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    
    @property
    def full_name(self) -> str:
        """Return user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        return self.username
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<User {self.username}>"


class Category(TimeStampMixin, SoftDeleteMixin, db.Model):
    """Task category entity."""
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), default="#6c757d")  # Default to secondary color
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="categories")
    tasks = relationship("Task", back_populates="category")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert category to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<Category {self.name}>"


class Task(TimeStampMixin, SoftDeleteMixin, db.Model):
    """Task entity class."""
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    parent_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    category = relationship("Category", back_populates="tasks")
    parent = relationship("Task", remote_side=[id], backref="subtasks")
    
    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if not self.due_date:
            return False
        if self.status == TaskStatus.DONE:
            return False
        return self.due_date < datetime.utcnow()
    
    @property
    def is_due_soon(self) -> bool:
        """Check if task is due soon (within 24 hours)."""
        if not self.due_date:
            return False
        if self.status == TaskStatus.DONE:
            return False
        now = datetime.utcnow()
        return now <= self.due_date <= (now + timedelta(hours=24))
    
    def complete(self) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.DONE
        self.completed_at = datetime.utcnow()
    
    def reopen(self) -> None:
        """Reopen a completed task."""
        self.status = TaskStatus.TODO
        self.completed_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority.name,
            'status': self.status.name,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'parent_id': self.parent_id,
            'is_overdue': self.is_overdue,
            'is_due_soon': self.is_due_soon,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<Task {self.title}>"


class TaskTag(db.Model):
    """Many-to-many relationship between tasks and tags."""
    __tablename__ = 'task_tags'
    
    task_id = Column(Integer, ForeignKey('tasks.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)
    
    # Relationships
    task = relationship("Task", backref="task_tags")
    tag = relationship("Tag", backref="task_tags")


class Tag(TimeStampMixin, db.Model):
    """Tag entity class."""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = relationship("User", backref="tags")
    tasks = relationship("Task", secondary="task_tags", backref="tags")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tag to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
        }
    
    def __repr__(self) -> str:
        return f"<Tag {self.name}>"
