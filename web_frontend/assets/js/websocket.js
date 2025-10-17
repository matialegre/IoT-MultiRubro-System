/**
 * IoT Multi-Rubro - WebSocket Connection
 * =======================================
 * Real-time data streaming from backend
 */

let ws = null;
let reconnectInterval = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 10;
const RECONNECT_DELAY = 3000; // 3 seconds

// ============================================
// WEBSOCKET INITIALIZATION
// ============================================
function initWebSocket() {
    connectWebSocket();
}

function connectWebSocket() {
    const wsUrl = 'ws://localhost:8000/ws/realtime';
    
    console.log('Connecting to WebSocket:', wsUrl);
    
    try {
        ws = new WebSocket(wsUrl);
        
        ws.onopen = onWebSocketOpen;
        ws.onmessage = onWebSocketMessage;
        ws.onerror = onWebSocketError;
        ws.onclose = onWebSocketClose;
        
    } catch (error) {
        console.error('WebSocket connection error:', error);
        scheduleReconnect();
    }
}

// ============================================
// WEBSOCKET EVENT HANDLERS
// ============================================
function onWebSocketOpen(event) {
    console.log('✓ WebSocket connected');
    reconnectAttempts = 0;
    updateConnectionStatus(true);
    
    // Clear reconnect interval if exists
    if (reconnectInterval) {
        clearInterval(reconnectInterval);
        reconnectInterval = null;
    }
}

function onWebSocketMessage(event) {
    try {
        const message = JSON.parse(event.data);
        handleMessage(message);
    } catch (error) {
        console.error('Error parsing WebSocket message:', error);
    }
}

function onWebSocketError(event) {
    console.error('WebSocket error:', event);
    updateConnectionStatus(false);
}

function onWebSocketClose(event) {
    console.log('WebSocket disconnected');
    updateConnectionStatus(false);
    
    // Attempt to reconnect
    scheduleReconnect();
}

// ============================================
// MESSAGE HANDLING
// ============================================
function handleMessage(message) {
    switch (message.type) {
        case 'sensor_data':
            handleSensorData(message);
            break;
        
        case 'alert':
            handleAlert(message);
            break;
        
        case 'device_status':
            handleDeviceStatus(message);
            break;
        
        case 'heartbeat':
            // Server keepalive, no action needed
            break;
        
        default:
            console.log('Unknown message type:', message.type);
    }
}

function handleSensorData(message) {
    const { device_id, device_name, value, unit, quality, timestamp } = message;
    
    // Update device value on dashboard
    updateDeviceValue(device_id, value, unit);
    
    // Update current values list
    updateCurrentValuesList(device_id, device_name, value, unit, timestamp);
    
    // Update chart if this device is selected
    if (window.charts) {
        window.charts.addRealtimeDataPoint(device_id, device_name, value, timestamp);
    }
    
    // Update device selector dropdown
    updateDeviceSelector(device_id, device_name);
}

function handleAlert(message) {
    const { severity, title, alert_message } = message;
    
    // Show notification
    if (window.dashboard) {
        window.dashboard.showNotification(
            `[${severity.toUpperCase()}] ${title}: ${alert_message}`,
            severity === 'critical' || severity === 'error' ? 'error' : 'warning'
        );
    }
    
    // Play alert sound
    playAlertSound(severity);
    
    // Reload alerts if on alerts page
    const alertsSection = document.getElementById('alerts-section');
    if (alertsSection && alertsSection.style.display !== 'none') {
        if (window.dashboard) {
            window.dashboard.loadAlerts();
        }
    }
}

function handleDeviceStatus(message) {
    const { device_id, status } = message;
    
    // Update device status on grid
    const deviceItem = document.querySelector(`[onclick*="${device_id}"]`);
    if (deviceItem) {
        deviceItem.className = `device-item ${status}`;
        const badge = deviceItem.querySelector('.badge');
        if (badge) {
            badge.className = `badge ${status === 'online' ? 'bg-success' : 'bg-danger'}`;
            badge.textContent = status === 'online' ? 'Online' : 'Offline';
        }
    }
}

// ============================================
// UI UPDATES
// ============================================
function updateDeviceValue(deviceId, value, unit) {
    const valueElement = document.getElementById(`device-value-${deviceId}`);
    const unitElement = document.getElementById(`device-unit-${deviceId}`);
    
    if (valueElement) {
        // Animate value change
        valueElement.style.transition = 'all 0.3s ease';
        valueElement.style.transform = 'scale(1.1)';
        valueElement.textContent = formatValue(value);
        
        setTimeout(() => {
            valueElement.style.transform = 'scale(1)';
        }, 300);
    }
    
    if (unitElement) {
        unitElement.textContent = unit || '';
    }
}

function updateCurrentValuesList(deviceId, deviceName, value, unit, timestamp) {
    const container = document.getElementById('current-values');
    if (!container) return;
    
    // Remove "waiting" message
    const waitingMsg = container.querySelector('.text-muted');
    if (waitingMsg) {
        waitingMsg.remove();
    }
    
    // Check if device already in list
    let item = document.getElementById(`current-${deviceId}`);
    
    if (!item) {
        // Create new item
        item = document.createElement('div');
        item.id = `current-${deviceId}`;
        item.className = 'list-group-item';
        container.appendChild(item);
    }
    
    // Update content with animation
    item.className = 'list-group-item fade-in';
    item.innerHTML = `
        <div class="current-value-item">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <div class="label">${deviceName}</div>
                    <div class="value">${formatValue(value)} <span class="device-unit">${unit || ''}</span></div>
                </div>
                <div class="text-end">
                    <span class="badge bg-success">Live</span>
                    <div class="timestamp">${formatTimestamp(timestamp)}</div>
                </div>
            </div>
        </div>
    `;
}

function updateDeviceSelector(deviceId, deviceName) {
    const select = document.getElementById('chart-device-select');
    if (!select) return;
    
    // Check if device already in selector
    const existingOption = select.querySelector(`option[value="${deviceId}"]`);
    if (existingOption) return;
    
    // Add new option
    const option = document.createElement('option');
    option.value = deviceId;
    option.textContent = `${deviceName} (${deviceId})`;
    select.appendChild(option);
}

function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');
    if (!statusElement) return;
    
    if (connected) {
        statusElement.innerHTML = '<i class="bi bi-circle-fill text-success pulse"></i> Conectado';
    } else {
        statusElement.innerHTML = '<i class="bi bi-circle-fill text-danger"></i> Desconectado';
    }
}

// ============================================
// RECONNECTION LOGIC
// ============================================
function scheduleReconnect() {
    if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
        console.error('Max reconnection attempts reached');
        if (window.dashboard) {
            window.dashboard.showNotification(
                'No se pudo reconectar al servidor. Por favor recargue la página.',
                'error'
            );
        }
        return;
    }
    
    if (reconnectInterval) return; // Already scheduled
    
    reconnectAttempts++;
    console.log(`Reconnecting in ${RECONNECT_DELAY/1000}s (attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`);
    
    reconnectInterval = setTimeout(() => {
        reconnectInterval = null;
        connectWebSocket();
    }, RECONNECT_DELAY);
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
function formatValue(value) {
    if (typeof value === 'number') {
        return value.toFixed(2);
    }
    return value;
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('es-AR');
}

function playAlertSound(severity) {
    // [Simulation] In production, play actual sound based on severity
    if (severity === 'critical') {
        // Play critical alert sound
        console.log('🔊 Critical alert sound');
    }
}

// ============================================
// CLEANUP ON PAGE UNLOAD
// ============================================
window.addEventListener('beforeunload', () => {
    if (ws) {
        ws.close();
    }
    if (reconnectInterval) {
        clearTimeout(reconnectInterval);
    }
});

// ============================================
// EXPORT FOR USE IN OTHER MODULES
// ============================================
window.websocket = {
    connect: connectWebSocket,
    disconnect: () => {
        if (ws) ws.close();
    },
    send: (data) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(data));
        }
    }
};
