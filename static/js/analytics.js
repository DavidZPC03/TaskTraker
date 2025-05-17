/**
 * JavaScript for analytics-related functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Setup export buttons
    setupExportButtons();
    
    // Setup refresh button
    setupRefreshButton();
    
    // Setup data polling (optional)
    // setupDataPolling();
});

/**
 * Setup export buttons functionality
 */
function setupExportButtons() {
    // Export as image button
    const exportImageBtn = document.getElementById('export-image');
    if (exportImageBtn) {
        exportImageBtn.addEventListener('click', function(e) {
            e.preventDefault();
            exportChartsAsImage();
        });
    }
    
    // Export raw data button
    const exportDataBtn = document.getElementById('export-data');
    if (exportDataBtn) {
        exportDataBtn.addEventListener('click', function(e) {
            e.preventDefault();
            exportRawData();
        });
    }
}

/**
 * Export charts as images
 */
function exportChartsAsImage() {
    // Get all canvas elements (charts)
    const chartCanvases = document.querySelectorAll('canvas');
    
    if (chartCanvases.length === 0) {
        showToast('Warning', 'No charts found to export', 'warning');
        return;
    }
    
    // We'll use this to create a zip file if multiple charts
    const chartImages = [];
    
    chartCanvases.forEach((canvas, index) => {
        try {
            const image = canvas.toDataURL('image/png');
            chartImages.push({
                name: `chart_${index + 1}.png`,
                data: image
            });
            
            // For simplicity, if only one chart, directly download it
            if (chartCanvases.length === 1) {
                const link = document.createElement('a');
                link.download = 'task_manager_chart.png';
                link.href = image;
                link.click();
            }
        } catch (error) {
            console.error('Error exporting chart:', error);
        }
    });
    
    // If multiple charts, would typically create a zip file
    // But for this implementation, we'll just download the first one
    if (chartImages.length > 1) {
        showToast('Info', `Exported ${chartImages.length} charts. In a full implementation, these would be zipped.`, 'info');
        
        // Download the first chart
        const link = document.createElement('a');
        link.download = 'task_manager_chart.png';
        link.href = chartImages[0].data;
        link.click();
    }
}

/**
 * Export raw analytics data
 */
function exportRawData() {
    // In a real implementation, this would call the server-side export
    // For now, we'll use the existing endpoint
    fetch('/profile/export-data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        showToast('Success', 'Data export has been scheduled. You will be notified when it is ready.', 'success');
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error', 'Failed to export data. Please try again.', 'danger');
    });
}

/**
 * Setup refresh button functionality
 */
function setupRefreshButton() {
    const refreshBtn = document.getElementById('refresh-analytics');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            // Show loading state
            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Refreshing...';
            
            // Reload the page after a short delay
            setTimeout(() => {
                window.location.reload();
            }, 500);
        });
    }
}

/**
 * Setup data polling for real-time updates
 * This is a more advanced feature that would periodically fetch updated data
 */
function setupDataPolling() {
    // This would be enabled in a production environment with real-time updates
    // For now, it's commented out
    
    /*
    const pollingInterval = 60000; // 1 minute
    
    // Function to update charts with new data
    const updateCharts = () => {
        fetch('/api/tasks/analytics', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Update charts with new data
            // This would require accessing the Chart instances and updating their data
            if (window.completionTrendChart) {
                window.completionTrendChart.data.datasets[0].data = data.completion_trend.data;
                window.completionTrendChart.update();
            }
            
            // More chart updates...
            
            console.log('Charts updated with latest data');
        })
        .catch(error => {
            console.error('Error updating analytics data:', error);
        });
    };
    
    // Set up the polling interval
    const pollingId = setInterval(updateCharts, pollingInterval);
    
    // Clean up on page unload
    window.addEventListener('beforeunload', () => {
        clearInterval(pollingId);
    });
    */
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
