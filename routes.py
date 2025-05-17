import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Any, Optional, Tuple, Union

from flask import (
    render_template, request, redirect, url_for,
    flash, jsonify, abort, g, session
)
from flask_login import (
    login_user, logout_user, current_user, login_required
)
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db
from models import User, Category, Task, Tag, TaskTag, TaskPriority, TaskStatus
from functional_utils import (
    filter_tasks, sort_tasks, get_task_stats,
    get_category_stats, get_overdue_tasks
)
from async_processor import (
    process_task_metrics_async, send_task_reminders_async,
    export_user_data_async
)

# ===== Helper Functions =====

def handle_db_error(e: Exception, operation: str) -> None:
    """Handle database errors uniformly."""
    logging.error(f"Database error during {operation}: {str(e)}")
    db.session.rollback()
    flash(f"An error occurred while {operation}. Please try again.", "danger")


# ===== Authentication Routes =====

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            flash('Username or email already exists', 'danger')
            return render_template('register.html')
        
        # Create new user
        try:
            new_user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password)
            )
            db.session.add(new_user)
            
            # Create default category for the user
            default_category = Category(
                name="General",
                description="Default category for tasks",
                color="#6c757d",
                user=new_user
            )
            db.session.add(default_category)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except SQLAlchemyError as e:
            handle_db_error(e, "creating user account")
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        if not all([username, password]):
            flash('Username and password are required', 'danger')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout route."""
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('index'))


# ===== Main Routes =====

@app.route('/')
def index():
    """Landing page route."""
    return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard route."""
    # Get task statistics using functional programming
    overdue_tasks = get_overdue_tasks(current_user.id)
    today_tasks = filter_tasks(current_user.tasks, lambda t: t.due_date and t.due_date.date() == datetime.utcnow().date())
    task_stats = get_task_stats(current_user.tasks)
    category_stats = get_category_stats(current_user.categories)
    
    # Process metrics asynchronously
    process_task_metrics_async(current_user.id)
    
    return render_template(
        'dashboard.html',
        task_stats=task_stats,
        category_stats=category_stats,
        overdue_tasks=overdue_tasks,
        today_tasks=today_tasks
    )


# ===== Task Routes =====

@app.route('/tasks')
@login_required
def tasks():
    """View all tasks."""
    status_filter = request.args.get('status')
    category_filter = request.args.get('category')
    priority_filter = request.args.get('priority')
    sort_by = request.args.get('sort_by', 'due_date')
    sort_order = request.args.get('sort_order', 'asc')
    
    # Get filters using functional programming
    tasks_list = current_user.tasks
    
    if status_filter:
        tasks_list = filter_tasks(tasks_list, lambda t: t.status.name == status_filter)
    
    if category_filter:
        tasks_list = filter_tasks(tasks_list, lambda t: t.category_id == int(category_filter))
    
    if priority_filter:
        tasks_list = filter_tasks(tasks_list, lambda t: t.priority.name == priority_filter)
    
    # Sort tasks using functional programming
    tasks_list = sort_tasks(tasks_list, sort_by, sort_order)
    
    # Get categories for filtering
    categories = Category.query.filter_by(user_id=current_user.id).all()
    
    return render_template(
        'tasks.html',
        tasks=tasks_list,
        categories=categories,
        priorities=TaskPriority,
        statuses=TaskStatus,
        current_filters={
            'status': status_filter,
            'category': category_filter,
            'priority': priority_filter,
            'sort_by': sort_by,
            'sort_order': sort_order
        }
    )


@app.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    """Create a new task."""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority', TaskPriority.MEDIUM.name)
        status = request.form.get('status', TaskStatus.TODO.name)
        due_date_str = request.form.get('due_date')
        category_id = request.form.get('category_id')
        parent_id = request.form.get('parent_id')
        
        if not title:
            flash('Task title is required', 'danger')
            return redirect(url_for('create_task'))
        
        try:
            # Parse due date if provided
            due_date = None
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    flash('Invalid date format', 'danger')
                    return redirect(url_for('create_task'))
            
            # Create task
            new_task = Task(
                title=title,
                description=description,
                priority=TaskPriority[priority],
                status=TaskStatus[status],
                due_date=due_date,
                user_id=current_user.id,
                category_id=category_id if category_id else None,
                parent_id=parent_id if parent_id else None
            )
            
            db.session.add(new_task)
            db.session.commit()
            
            flash('Task created successfully', 'success')
            return redirect(url_for('tasks'))
        except SQLAlchemyError as e:
            handle_db_error(e, "creating task")
    
    # Get categories and parent tasks for the form
    categories = Category.query.filter_by(user_id=current_user.id).all()
    parent_tasks = Task.query.filter_by(
        user_id=current_user.id, 
        parent_id=None
    ).all()
    
    return render_template(
        'task_detail.html',
        task=None,
        categories=categories,
        parent_tasks=parent_tasks,
        priorities=TaskPriority,
        statuses=TaskStatus,
        is_new=True
    )


@app.route('/tasks/<int:task_id>')
@login_required
def view_task(task_id):
    """View task details."""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    return render_template('task_detail.html', task=task, is_new=False)


@app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """Edit an existing task."""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority')
        status = request.form.get('status')
        due_date_str = request.form.get('due_date')
        category_id = request.form.get('category_id')
        parent_id = request.form.get('parent_id')
        
        if not title:
            flash('Task title is required', 'danger')
            return redirect(url_for('edit_task', task_id=task_id))
        
        try:
            # Update task fields
            task.title = title
            task.description = description
            task.priority = TaskPriority[priority]
            
            # Handle status change
            old_status = task.status
            new_status = TaskStatus[status]
            task.status = new_status
            
            # Update completed_at if status changed to DONE
            if old_status != TaskStatus.DONE and new_status == TaskStatus.DONE:
                task.completed_at = datetime.utcnow()
            elif old_status == TaskStatus.DONE and new_status != TaskStatus.DONE:
                task.completed_at = None
            
            # Parse due date if provided
            if due_date_str:
                try:
                    task.due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    flash('Invalid date format', 'danger')
                    return redirect(url_for('edit_task', task_id=task_id))
            else:
                task.due_date = None
            
            # Update relationships
            task.category_id = category_id if category_id else None
            
            # Check for circular parent-child relationships
            if parent_id and int(parent_id) != task.id:
                potential_parent = Task.query.get(parent_id)
                # Check if potential parent is not a child of current task
                if potential_parent and not is_descendant(potential_parent, task):
                    task.parent_id = parent_id
            else:
                task.parent_id = None
            
            db.session.commit()
            flash('Task updated successfully', 'success')
            return redirect(url_for('tasks'))
        except SQLAlchemyError as e:
            handle_db_error(e, "updating task")
    
    # Get categories and parent tasks for the form
    categories = Category.query.filter_by(user_id=current_user.id).all()
    parent_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.parent_id.is_(None),
        Task.id != task_id
    ).all()
    
    return render_template(
        'task_detail.html',
        task=task,
        categories=categories,
        parent_tasks=parent_tasks,
        priorities=TaskPriority,
        statuses=TaskStatus,
        is_new=False
    )


def is_descendant(task, potential_ancestor):
    """Check if a task is a descendant of another task."""
    if not task.parent_id:
        return False
    if task.parent_id == potential_ancestor.id:
        return True
    return is_descendant(task.parent, potential_ancestor)


@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """Delete a task."""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    
    try:
        # Soft delete
        task.soft_delete()
        db.session.commit()
        flash('Task deleted successfully', 'success')
    except SQLAlchemyError as e:
        handle_db_error(e, "deleting task")
    
    return redirect(url_for('tasks'))


@app.route('/tasks/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task_status(task_id):
    """Toggle task status between TODO and DONE."""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    
    try:
        if task.status == TaskStatus.DONE:
            task.reopen()
            message = 'Task reopened'
        else:
            task.complete()
            message = 'Task completed'
        
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': message})
        
        flash(message, 'success')
        return redirect(request.referrer or url_for('tasks'))
    except SQLAlchemyError as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Database error'})
        
        flash('An error occurred while updating task status', 'danger')
        return redirect(request.referrer or url_for('tasks'))


# ===== Category Routes =====

@app.route('/categories')
@login_required
def categories():
    """View all categories."""
    categories_list = Category.query.filter_by(user_id=current_user.id, is_deleted=False).all()
    return render_template('categories.html', categories=categories_list)


@app.route('/categories/create', methods=['GET', 'POST'])
@login_required
def create_category():
    """Create a new category."""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        color = request.form.get('color', '#6c757d')
        
        if not name:
            flash('Category name is required', 'danger')
            return redirect(url_for('create_category'))
        
        try:
            new_category = Category(
                name=name,
                description=description,
                color=color,
                user_id=current_user.id
            )
            
            db.session.add(new_category)
            db.session.commit()
            
            flash('Category created successfully', 'success')
            return redirect(url_for('categories'))
        except SQLAlchemyError as e:
            handle_db_error(e, "creating category")
    
    return render_template('categories.html', is_new=True)


@app.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    """Edit an existing category."""
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        color = request.form.get('color')
        
        if not name:
            flash('Category name is required', 'danger')
            return redirect(url_for('edit_category', category_id=category_id))
        
        try:
            category.name = name
            category.description = description
            category.color = color
            
            db.session.commit()
            flash('Category updated successfully', 'success')
            return redirect(url_for('categories'))
        except SQLAlchemyError as e:
            handle_db_error(e, "updating category")
    
    return render_template('categories.html', category=category, is_new=False)


@app.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    """Delete a category."""
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first_or_404()
    
    try:
        # Check if category has tasks
        tasks_count = Task.query.filter_by(category_id=category_id).count()
        
        if tasks_count > 0:
            # Soft delete
            category.soft_delete()
            flash('Category deleted. Tasks have been preserved.', 'info')
        else:
            # Hard delete
            db.session.delete(category)
            flash('Category deleted successfully', 'success')
        
        db.session.commit()
    except SQLAlchemyError as e:
        handle_db_error(e, "deleting category")
    
    return redirect(url_for('categories'))


# ===== Analytics Routes =====

@app.route('/analytics')
@login_required
def analytics():
    """View task analytics."""
    # Trigger async processing of task metrics
    process_task_metrics_async(current_user.id)
    
    # Get task statistics using functional programming
    task_stats = get_task_stats(current_user.tasks)
    category_stats = get_category_stats(current_user.categories)
    
    # Get tasks completed by day for the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    completed_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.completed_at.isnot(None),
        Task.completed_at >= thirty_days_ago
    ).all()
    
    # Process data for charts
    completion_by_day = {}
    for task in completed_tasks:
        day = task.completed_at.strftime('%Y-%m-%d')
        completion_by_day[day] = completion_by_day.get(day, 0) + 1
    
    # Fill in missing days
    all_days = {}
    for i in range(30):
        day = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
        all_days[day] = completion_by_day.get(day, 0)
    
    # Sort days
    sorted_days = sorted(all_days.items())
    
    return render_template(
        'analytics.html',
        task_stats=task_stats,
        category_stats=category_stats,
        completion_dates=[day for day, _ in sorted_days],
        completion_counts=[count for _, count in sorted_days]
    )


# ===== Profile Routes =====

@app.route('/profile')
@login_required
def profile():
    """View user profile."""
    return render_template('profile.html', user=current_user)


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile."""
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        
        try:
            # Check if email is already taken by another user
            if email != current_user.email:
                existing_user = User.query.filter_by(email=email).first()
                if existing_user:
                    flash('Email is already taken', 'danger')
                    return redirect(url_for('edit_profile'))
            
            # Update user profile
            current_user.first_name = first_name
            current_user.last_name = last_name
            current_user.email = email
            
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('profile'))
        except SQLAlchemyError as e:
            handle_db_error(e, "updating profile")
    
    return render_template('profile.html', user=current_user, edit=True)


@app.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password."""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        flash('All password fields are required', 'danger')
        return redirect(url_for('profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match', 'danger')
        return redirect(url_for('profile'))
    
    if not check_password_hash(current_user.password_hash, current_password):
        flash('Current password is incorrect', 'danger')
        return redirect(url_for('profile'))
    
    try:
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash('Password changed successfully', 'success')
    except SQLAlchemyError as e:
        handle_db_error(e, "changing password")
    
    return redirect(url_for('profile'))


@app.route('/profile/export-data', methods=['POST'])
@login_required
def export_data():
    """Export user data asynchronously."""
    # Schedule async export
    export_user_data_async(current_user.id)
    flash('Your data export has been scheduled. You will be notified when it is ready.', 'info')
    return redirect(url_for('profile'))


# ===== Error Handlers =====

@app.errorhandler(404)
def page_not_found(e):
    """404 Page not found handler."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """500 Internal server error handler."""
    return render_template('500.html'), 500


# ===== API Routes =====

@app.route('/api/tasks/overdue', methods=['GET'])
@login_required
def api_overdue_tasks():
    """API endpoint to get overdue tasks."""
    overdue_tasks = get_overdue_tasks(current_user.id)
    return jsonify({
        'success': True,
        'count': len(overdue_tasks),
        'tasks': [task.to_dict() for task in overdue_tasks]
    })


@app.route('/api/tasks/reminder', methods=['POST'])
@login_required
def api_send_reminders():
    """API endpoint to send task reminders asynchronously."""
    send_task_reminders_async(current_user.id)
    return jsonify({
        'success': True,
        'message': 'Reminders scheduled to be sent'
    })
