/**
 * Main JavaScript file for Task Manager application
 * Contains common functionality used across the application
 */

// Initialize Feather icons when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Replace feather icons
    feather.replace({ 'aria-hidden': 'true' });
    
    // Setup auto-dismiss for alerts
    setupAlertAutoDismiss();
    
    // Setup form validation
    setupFormValidation();
    
    // Initialize tooltips
    initTooltips();
});

/**
 * Set up auto-dismissing alerts after a delay
 */
function setupAlertAutoDismiss() {
    // Auto-dismiss flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            // Create a dismiss event
            const dismissEvent = new bootstrap.Alert(alert);
            dismissEvent.close();
        }, 5000);
    });
}

/**
 * Set up form validation for all forms with the 'needs-validation' class
 */
function setupFormValidation() {
    // Fetch all forms we want to apply custom validation to
    const forms = document.querySelectorAll('.needs-validation');
    
    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

/**
 * Toggle the task status via AJAX
 * @param {number} taskId - The ID of the task to toggle
 * @param {Element} buttonElement - The button element that was clicked
 */
function toggleTaskStatus(taskId, buttonElement) {
    // Show loading state
    const originalHTML = buttonElement.innerHTML;
    buttonElement.disabled = true;
    buttonElement.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
    
    // Send AJAX request
    fetch(`/tasks/${taskId}/toggle`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Get the table row or list item containing the button
            const container = buttonElement.closest('tr') || buttonElement.closest('.list-group-item');
            
            // Update visual state based on task status
            if (data.message.includes('completed')) {
                buttonElement.innerHTML = '<i data-feather="refresh-cw"></i>';
                buttonElement.classList.remove('btn-outline-success');
                buttonElement.classList.add('btn-outline-secondary');
                if (container) {
                    container.classList.add('bg-light');
                    // Add completed class or visual indicator
                    const titleElement = container.querySelector('.task-title');
                    if (titleElement) {
                        titleElement.classList.add('text-decoration-line-through');
                    }
                }
            } else {
                buttonElement.innerHTML = '<i data-feather="check"></i>';
                buttonElement.classList.remove('btn-outline-secondary');
                buttonElement.classList.add('btn-outline-success');
                if (container) {
                    container.classList.remove('bg-light');
                    // Remove completed class or visual indicator
                    const titleElement = container.querySelector('.task-title');
                    if (titleElement) {
                        titleElement.classList.remove('text-decoration-line-through');
                    }
                }
            }
            
            // Re-initialize feather icons
            feather.replace({ 'aria-hidden': 'true' });
            
            // Show success message
            showToast('Success', data.message, 'success');
        } else {
            buttonElement.innerHTML = originalHTML;
            showToast('Error', 'Failed to update task status', 'danger');
        }
        
        // Re-enable the button
        buttonElement.disabled = false;
    })
    .catch(error => {
        console.error('Error:', error);
        buttonElement.innerHTML = originalHTML;
        buttonElement.disabled = false;
        showToast('Error', 'An error occurred while updating task status', 'danger');
    });
}

/**
 * Show a toast notification
 * @param {string} title - The title of the toast
 * @param {string} message - The message to display
 * @param {string} type - The type of toast (success, danger, warning, info)
 */
function showToast(title, message, type = 'info') {
    // Check if toast container exists, if not create it
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastElement = document.createElement('div');
    toastElement.className = `toast align-items-center text-white bg-${type} border-0`;
    toastElement.setAttribute('role', 'alert');
    toastElement.setAttribute('aria-live', 'assertive');
    toastElement.setAttribute('aria-atomic', 'true');
    
    // Create toast content
    toastElement.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <strong>${title}:</strong> ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Add toast to container
    toastContainer.appendChild(toastElement);
    
    // Initialize and show the toast
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 5000
    });
    toast.show();
    
    // Remove toast from DOM after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

/**
 * Format date for display
 * @param {string|Date} dateString - The date to format
 * @param {boolean} includeTime - Whether to include time in the formatted date
 * @returns {string} - The formatted date string
 */
function formatDate(dateString, includeTime = false) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    
    if (includeTime) {
        options.hour = '2-digit';
        options.minute = '2-digit';
    }
    
    return date.toLocaleDateString('en-US', options);
}

/**
 * Check if a task is overdue
 * @param {string|Date} dueDate - The due date to check
 * @param {string} status - The current status of the task
 * @returns {boolean} - True if the task is overdue, false otherwise
 */
function isTaskOverdue(dueDate, status) {
    if (!dueDate || status === 'DONE') return false;
    
    const now = new Date();
    const due = new Date(dueDate);
    
    return due < now;
}

/**
 * Check if a task is due soon (within 24 hours)
 * @param {string|Date} dueDate - The due date to check
 * @param {string} status - The current status of the task
 * @returns {boolean} - True if the task is due soon, false otherwise
 */
function isTaskDueSoon(dueDate, status) {
    if (!dueDate || status === 'DONE') return false;
    
    const now = new Date();
    const due = new Date(dueDate);
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    return now <= due && due <= tomorrow;
}
