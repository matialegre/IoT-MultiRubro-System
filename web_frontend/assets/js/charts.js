/**
 * IoT Multi-Rubro - Chart Management
 * ===================================
 * Handles real-time chart updates using Chart.js
 */

let realtimeChart = null;
const MAX_DATA_POINTS = 50;
const chartData = new Map(); // device_id -> {labels: [], data: []}

// ============================================
// CHART INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initRealtimeChart();
    setupChartControls();
});

function initRealtimeChart() {
    const ctx = document.getElementById('realtime-chart');
    if (!ctx) return;
    
    realtimeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
                title: {
                    display: false
                },
                tooltip: {
                    enabled: true,
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Tiempo'
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 0
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Valor'
                    }
                }
            },
            animation: {
                duration: 750,
                easing: 'easeInOutQuart'
            }
        }
    });
}

function setupChartControls() {
    const deviceSelect = document.getElementById('chart-device-select');
    if (!deviceSelect) return;
    
    deviceSelect.addEventListener('change', (e) => {
        const deviceId = e.target.value;
        if (deviceId) {
            loadDeviceHistory(deviceId);
        } else {
            clearChart();
        }
    });
}

// ============================================
// CHART DATA MANAGEMENT
// ============================================
async function loadDeviceHistory(deviceId) {
    try {
        const data = await window.dashboard.fetchAPI(`/data/${deviceId}?limit=50`);
        updateDeviceChart(data);
    } catch (error) {
        console.error('Error loading device history:', error);
    }
}

function updateDeviceChart(data) {
    if (!realtimeChart || !data.data) return;
    
    const labels = data.data.map(d => formatChartTime(d.timestamp));
    const values = data.data.map(d => d.value);
    
    // Update chart
    realtimeChart.data.labels = labels;
    realtimeChart.data.datasets = [{
        label: `${data.device_name} (${data.device_type})`,
        data: values,
        borderColor: getDeviceColor(data.device_id),
        backgroundColor: getDeviceColor(data.device_id, 0.1),
        borderWidth: 2,
        tension: 0.4,
        fill: true,
        pointRadius: 3,
        pointHoverRadius: 5
    }];
    
    realtimeChart.update();
    
    // Store in map for real-time updates
    chartData.set(data.device_id, {
        labels: labels,
        data: values,
        name: data.device_name,
        type: data.device_type
    });
}

function addRealtimeDataPoint(deviceId, deviceName, value, timestamp) {
    if (!realtimeChart) return;
    
    // Check if this device is currently being displayed
    const deviceSelect = document.getElementById('chart-device-select');
    if (deviceSelect && deviceSelect.value !== deviceId) {
        // Not the active device, just store the data
        updateStoredData(deviceId, deviceName, value, timestamp);
        return;
    }
    
    // Get or create dataset
    let dataset = realtimeChart.data.datasets[0];
    if (!dataset) {
        dataset = {
            label: deviceName,
            data: [],
            borderColor: getDeviceColor(deviceId),
            backgroundColor: getDeviceColor(deviceId, 0.1),
            borderWidth: 2,
            tension: 0.4,
            fill: true,
            pointRadius: 3,
            pointHoverRadius: 5
        };
        realtimeChart.data.datasets.push(dataset);
    }
    
    // Add new data point
    const timeLabel = formatChartTime(timestamp);
    realtimeChart.data.labels.push(timeLabel);
    dataset.data.push(value);
    
    // Keep only MAX_DATA_POINTS
    if (realtimeChart.data.labels.length > MAX_DATA_POINTS) {
        realtimeChart.data.labels.shift();
        dataset.data.shift();
    }
    
    // Update chart
    realtimeChart.update('none'); // No animation for real-time updates
    
    // Update stored data
    updateStoredData(deviceId, deviceName, value, timestamp);
}

function updateStoredData(deviceId, deviceName, value, timestamp) {
    let stored = chartData.get(deviceId);
    
    if (!stored) {
        stored = {
            labels: [],
            data: [],
            name: deviceName
        };
        chartData.set(deviceId, stored);
    }
    
    stored.labels.push(formatChartTime(timestamp));
    stored.data.push(value);
    
    // Keep only MAX_DATA_POINTS
    if (stored.labels.length > MAX_DATA_POINTS) {
        stored.labels.shift();
        stored.data.shift();
    }
}

function clearChart() {
    if (!realtimeChart) return;
    
    realtimeChart.data.labels = [];
    realtimeChart.data.datasets = [];
    realtimeChart.update();
}

// ============================================
// DEVICE COLOR ASSIGNMENT
// ============================================
const deviceColors = [
    '#0d6efd', // Blue
    '#198754', // Green
    '#ffc107', // Yellow
    '#dc3545', // Red
    '#0dcaf0', // Cyan
    '#6f42c1', // Purple
    '#fd7e14', // Orange
    '#20c997', // Teal
];

function getDeviceColor(deviceId, alpha = 1) {
    // Generate consistent color based on device ID
    let hash = 0;
    for (let i = 0; i < deviceId.length; i++) {
        hash = deviceId.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    const index = Math.abs(hash) % deviceColors.length;
    const color = deviceColors[index];
    
    if (alpha < 1) {
        // Convert hex to rgba
        const r = parseInt(color.slice(1, 3), 16);
        const g = parseInt(color.slice(3, 5), 16);
        const b = parseInt(color.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
    
    return color;
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
function formatChartTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('es-AR', { 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
    });
}

// ============================================
// MULTI-DEVICE CHART (Optional)
// ============================================
function addDeviceToChart(deviceId, deviceName, deviceType) {
    if (!realtimeChart) return;
    
    // Check if device already in chart
    const existingDataset = realtimeChart.data.datasets.find(
        ds => ds.deviceId === deviceId
    );
    
    if (existingDataset) return;
    
    // Add new dataset
    const dataset = {
        label: `${deviceName} (${deviceType})`,
        data: [],
        deviceId: deviceId,
        borderColor: getDeviceColor(deviceId),
        backgroundColor: getDeviceColor(deviceId, 0.1),
        borderWidth: 2,
        tension: 0.4,
        fill: true,
        pointRadius: 3,
        pointHoverRadius: 5
    };
    
    realtimeChart.data.datasets.push(dataset);
    realtimeChart.update();
}

function removeDeviceFromChart(deviceId) {
    if (!realtimeChart) return;
    
    const index = realtimeChart.data.datasets.findIndex(
        ds => ds.deviceId === deviceId
    );
    
    if (index !== -1) {
        realtimeChart.data.datasets.splice(index, 1);
        realtimeChart.update();
    }
}

// ============================================
// EXPORT FOR USE IN OTHER MODULES
// ============================================
window.charts = {
    updateDeviceChart,
    addRealtimeDataPoint,
    clearChart,
    addDeviceToChart,
    removeDeviceFromChart
};
