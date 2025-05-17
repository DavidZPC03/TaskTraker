/**
 * JavaScript for tasks-related functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle the delete task modal
    setupDeleteTaskModal();
    
    // Setup task toggling
    setupTaskToggling();
    
    // Setup filter form
    setupFilterForm();
    
    // Setup due date validation
    setupDueDateValidation();
});

/**
 * Setup delete task modal - populate data attributes
 */
function setupDeleteTaskModal() {
    const deleteModal = document.getElementById('deleteModal');
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function(event) {
            // Button that triggered the modal
            const button = event.relatedTarget;
            
            // Extract task info from data attributes
            const taskId = button.getAttribute('data-task-id');
            const taskTitle = button.getAttribute('data-task-title');
            
            // Update the modal's content
            const taskTitleElement = deleteModal.querySelector('#task-title');
            const deleteForm = deleteModal.querySelector('#delete-form');
            
            taskTitleElement.textContent = taskTitle;
            deleteForm.action = `/tasks/${taskId}/delete`;
        });
    }
}

/**
 * Setup task toggle functionality with AJAX
 */
function setupTaskToggling() {
    // Get all toggle forms
    const toggleForms = document.querySelectorAll('.toggle-form');
    
    toggleForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const url = this.action;
            const button = this.querySelector('button');
            
            // Send AJAX request
            fetch(url, {
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
                    const row = button.closest('tr');
                    
                    if (row) {
                        // Update button icon
                        const icon = button.querySelector('i');
                        if (data.message.includes('completed')) {
                            icon.setAttribute('data-feather', 'refresh-cw');
                            row.classList.add('table-success');
                            button.classList.remove('btn-outline-success');
                            button.classList.add('btn-outline-secondary');
                            
                            // Update status badge
                            const statusBadge = row.querySelector('td:nth-child(4) .badge');
                            if (statusBadge) {
                                statusBadge.className = 'badge bg-success';
                                statusBadge.textContent = 'DONE';
                            }
                        } else {
                            icon.setAttribute('data-feather', 'check');
                            row.classList.remove('table-success');
                            button.classList.remove('btn-outline-secondary');
                            button.classList.add('btn-outline-success');
                            
                            // Update status badge
                            const statusBadge = row.querySelector('td:nth-child(4) .badge');
                            if (statusBadge) {
                                statusBadge.className = 'badge bg-secondary';
                                statusBadge.textContent = 'TODO';
                            }
                        }
                        
                        // Replace feather icons
                        feather.replace();
                    }
                    
                    // Show success message using toast
                    showToast('Success', data.message, 'success');
                } else {
                    showToast('Error', 'Failed to update task status', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Error', 'An error occurred while updating task status', 'danger');
            });
        });
    });
}

/**
 * Setup filter form functionality
 */
function setupFilterForm() {
    // Clear filters button
    const clearFiltersBtn = document.getElementById('clear-filters');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            const filterForm = document.getElementById('filter-form');
            const selects = filterForm.querySelectorAll('select');
            
            // Reset all select elements
            selects.forEach(select => {
                select.value = '';
            });
            
            // Default sort options
            const sortBySelect = document.getElementById('sort_by');
            const sortOrderSelect = document.getElementById('sort_order');
            
            if (sortBySelect) sortBySelect.value = 'due_date';
            if (sortOrderSelect) sortOrderSelect.value = 'asc';
            
            // Submit the form
            filterForm.submit();
        });
    }
    
    // Auto-submit on select change (optional)
    const filterSelects = document.querySelectorAll('#filter-form select');
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            // Uncomment the next line to enable auto-submit on change
            // document.getElementById('filter-form').submit();
        });
    });
}

/**
 * Setup validation for due date field
 */
function setupDueDateValidation() {
    const dueDateInput = document.getElementById('due_date');
    if (dueDateInput) {
        dueDateInput.addEventListener('change', function() {
            const now = new Date();
            const selectedDate = new Date(this.value);
            
            // Reset validation styles
            this.classList.remove('is-invalid');
            
            // Check if date is in the past
            if (selectedDate < now) {
                // Add warning class but don't prevent submission
                this.classList.add('is-invalid');
                
                // Show warning message
                let warningElement = document.getElementById('due-date-warning');
                if (!warningElement) {
                    warningElement = document.createElement('div');
                    warningElement.id = 'due-date-warning';
                    warningElement.className = 'invalid-feedback';
                    warningElement.textContent = 'Warning: The selected date is in the past.';
                    this.parentNode.appendChild(warningElement);
                }
            }
        });
    }
}

/**
 * Show a toast notification - implemented if main.js doesn't load
 */
function showToast(title, message, type = 'info') {
    // Check if the main.js showToast function exists
    if (typeof window.showToast === 'function') {
        window.showToast(title, message, type);
        return;
    }
    
    // Fallback implementation
    alert(`${title}: ${message}`);
}
