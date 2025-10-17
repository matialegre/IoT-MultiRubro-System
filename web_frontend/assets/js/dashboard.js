/**
 * IoT Multi-Rubro Dashboard - Main Controller
 * =============================================
 * Handles UI interactions, data fetching, and page navigation
 */

const API_BASE = 'http://localhost:8000/api';
let refreshInterval = null;
let currentSection = 'dashboard';

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    console.log('IoT Dashboard initializing...');
    
    // Setup navigation
    setupNavigation();
    
    // Setup modals
    setupModals();
    
    // Load initial data
    loadDashboard();
    
    // Start auto-refresh
    startAutoRefresh();
    
    // Initialize WebSocket
    initWebSocket();
    
    console.log('✓ Dashboard initialized');
});

// ============================================
// NAVIGATION
// ============================================
function setupNavigation() {
    document.querySelectorAll('.nav-link[data-section]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = e.currentTarget.dataset.section;
            navigateToSection(section);
        });
    });
}

function navigateToSection(section) {
    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-section="${section}"]`).classList.add('active');
    
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(sec => {
        sec.style.display = 'none';
    });
    
    // Show target section
    document.getElementById(`${section}-section`).style.display = 'block';
    
    // Load section data
    currentSection = section;
    loadSectionData(section);
}

function loadSectionData(section) {
    switch(section) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'devices':
            loadDevices();
            break;
        case 'rules':
            loadRules();
            break;
        case 'alerts':
            loadAlerts();
            break;
    }
}

// ============================================
// DASHBOARD DATA
// ============================================
async function loadDashboard() {
    try {
        // Load statistics
        const stats = await fetchAPI('/stats');
        updateStatistics(stats);
        
        // Load devices
        const devices = await fetchAPI('/devices');
        updateDeviceGrid(devices);
        
        // Load alerts
        const alerts = await fetchAPI('/alerts?unresolved_only=true');
        updateAlertCount(alerts.length);
        
        // Load rules
        const rules = await fetchAPI('/rules?active_only=true');
        document.getElementById('stat-active-rules').textContent = rules.length;
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showNotification('Error cargando datos del dashboard', 'error');
    }
}

function updateStatistics(stats) {
    document.getElementById('stat-online-devices').textContent = stats.devices.online;
    document.getElementById('stat-active-alerts').textContent = stats.alerts.total;
    document.getElementById('stat-data-rate').textContent = stats.data.rate_per_minute;
}

function updateDeviceGrid(devices) {
    const grid = document.getElementById('device-grid');
    
    if (devices.length === 0) {
        grid.innerHTML = `
            <div class="col-12 text-center text-muted py-5">
                <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                <p>No hay dispositivos registrados</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = devices.map(device => `
        <div class="col-lg-3 col-md-4 col-sm-6">
            <div class="device-item ${device.status}" onclick="showDeviceDetails('${device.device_id}')">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                        <div class="device-name">${device.name}</div>
                        <div class="device-type">
                            <i class="bi bi-tag"></i> ${getDeviceTypeLabel(device.device_type)}
                        </div>
                    </div>
                    <span class="badge ${device.status === 'online' ? 'bg-success' : 'bg-danger'}">
                        ${device.status === 'online' ? 'Online' : 'Offline'}
                    </span>
                </div>
                <div class="device-value" id="device-value-${device.device_id}">--</div>
                <div class="device-unit" id="device-unit-${device.device_id}">Esperando datos...</div>
                <div class="mt-2 small text-muted">
                    <i class="bi bi-clock"></i> ${device.last_seen ? formatTimestamp(device.last_seen) : 'Nunca'}
                </div>
            </div>
        </div>
    `).join('');
}

function getDeviceTypeLabel(type) {
    const labels = {
        'temperature': 'Temperatura',
        'humidity': 'Humedad',
        'motion': 'Movimiento',
        'weight': 'Peso',
        'flow': 'Flujo',
        'soil_moisture': 'Humedad Suelo',
        'luminosity': 'Luminosidad',
        'distance': 'Distancia'
    };
    return labels[type] || type;
}

async function showDeviceDetails(deviceId) {
    try {
        const data = await fetchAPI(`/data/${deviceId}?limit=50`);
        
        // Update chart
        updateDeviceChart(data);
        
        // Show in dropdown
        document.getElementById('chart-device-select').value = deviceId;
        
    } catch (error) {
        console.error('Error loading device details:', error);
    }
}

// ============================================
// DEVICES MANAGEMENT
// ============================================
async function loadDevices() {
    try {
        const devices = await fetchAPI('/devices');
        updateDevicesTable(devices);
    } catch (error) {
        console.error('Error loading devices:', error);
    }
}

function updateDevicesTable(devices) {
    const tbody = document.querySelector('#devices-table tbody');
    
    if (devices.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted py-4">
                    No hay dispositivos registrados
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = devices.map(device => `
        <tr>
            <td><code>${device.device_id}</code></td>
            <td>${device.name}</td>
            <td>${getDeviceTypeLabel(device.device_type)}</td>
            <td><span class="badge bg-secondary">${device.rubro || 'N/A'}</span></td>
            <td>${device.location || '-'}</td>
            <td>
                <span class="badge ${device.status === 'online' ? 'bg-success' : 'bg-danger'}">
                    ${device.status}
                </span>
            </td>
            <td>${device.last_seen ? formatTimestamp(device.last_seen) : 'Nunca'}</td>
            <td>
                <button class="btn btn-sm btn-info" onclick="viewDeviceHistory('${device.device_id}')">
                    <i class="bi bi-graph-up"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteDevice('${device.device_id}')">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

async function viewDeviceHistory(deviceId) {
    navigateToSection('dashboard');
    showDeviceDetails(deviceId);
}

async function deleteDevice(deviceId) {
    if (!confirm(`¿Eliminar dispositivo ${deviceId}?`)) return;
    
    try {
        await fetchAPI(`/devices/${deviceId}`, { method: 'DELETE' });
        showNotification('Dispositivo eliminado', 'success');
        loadDevices();
    } catch (error) {
        showNotification('Error eliminando dispositivo', 'error');
    }
}

// ============================================
// RULES MANAGEMENT
// ============================================
async function loadRules() {
    try {
        const rules = await fetchAPI('/rules');
        updateRulesList(rules);
    } catch (error) {
        console.error('Error loading rules:', error);
    }
}

function updateRulesList(rules) {
    const list = document.getElementById('rules-list');
    
    if (rules.length === 0) {
        list.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="bi bi-gear fs-1 d-block mb-2"></i>
                <p>No hay reglas configuradas</p>
            </div>
        `;
        return;
    }
    
    list.innerHTML = rules.map(rule => `
        <div class="rule-item ${rule.is_active ? 'active' : 'inactive'}">
            <div class="d-flex justify-content-between align-items-start mb-2">
                <div>
                    <h6 class="mb-1">
                        ${rule.name}
                        ${rule.is_active ? 
                            '<span class="badge bg-success ms-2">Activa</span>' : 
                            '<span class="badge bg-secondary ms-2">Inactiva</span>'}
                    </h6>
                    <p class="text-muted small mb-2">${rule.description || ''}</p>
                </div>
                <div class="btn-group">
                    <button class="btn btn-sm btn-outline-primary" onclick="toggleRule(${rule.id}, ${!rule.is_active})">
                        <i class="bi bi-${rule.is_active ? 'pause' : 'play'}-fill"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteRule(${rule.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6 mb-2">
                    <small class="text-muted d-block mb-1"><strong>Condición:</strong></small>
                    <div class="rule-condition">
                        ${formatCondition(rule.condition)}
                    </div>
                </div>
                <div class="col-md-6 mb-2">
                    <small class="text-muted d-block mb-1"><strong>Acción:</strong></small>
                    <div class="rule-action">
                        ${formatAction(rule.action)}
                    </div>
                </div>
            </div>
            
            <div class="mt-2 small text-muted">
                <i class="bi bi-lightning-fill"></i> Activada ${rule.trigger_count} veces
                ${rule.last_triggered ? ` | Última: ${formatTimestamp(rule.last_triggered)}` : ''}
            </div>
        </div>
    `).join('');
}

function formatCondition(condition) {
    if (condition.and) {
        return condition.and.map(c => formatSimpleCondition(c)).join(' AND ');
    }
    if (condition.or) {
        return condition.or.map(c => formatSimpleCondition(c)).join(' OR ');
    }
    return formatSimpleCondition(condition);
}

function formatSimpleCondition(condition) {
    return `${condition.device_id} ${condition.operator} ${condition.value}`;
}

function formatAction(action) {
    if (action.type === 'alert') {
        return `Alerta [${action.severity}]: ${action.message}`;
    }
    if (action.type === 'actuate') {
        return `Controlar ${action.target}: ${action.command}`;
    }
    if (action.type === 'notify') {
        return `Notificar vía ${action.channel}`;
    }
    return JSON.stringify(action);
}

async function toggleRule(ruleId, activate) {
    try {
        // This would require updating the rule via PUT
        showNotification('Función en desarrollo', 'info');
    } catch (error) {
        showNotification('Error actualizando regla', 'error');
    }
}

async function deleteRule(ruleId) {
    if (!confirm('¿Eliminar esta regla?')) return;
    
    try {
        await fetchAPI(`/rules/${ruleId}`, { method: 'DELETE' });
        showNotification('Regla eliminada', 'success');
        loadRules();
    } catch (error) {
        showNotification('Error eliminando regla', 'error');
    }
}

// ============================================
// ALERTS MANAGEMENT
// ============================================
async function loadAlerts() {
    try {
        const alerts = await fetchAPI('/alerts?limit=50');
        updateAlertsList(alerts);
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

function updateAlertsList(alerts) {
    const list = document.getElementById('alerts-list');
    
    if (alerts.length === 0) {
        list.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="bi bi-check-circle fs-1 d-block mb-2"></i>
                <p>No hay alertas activas</p>
            </div>
        `;
        return;
    }
    
    list.innerHTML = alerts.map(alert => `
        <div class="alert-item severity-${alert.severity} ${alert.is_acknowledged ? 'acknowledged' : ''}">
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <h6 class="mb-1">
                        <i class="bi bi-exclamation-${alert.severity === 'critical' ? 'octagon' : 'triangle'}-fill"></i>
                        ${alert.title}
                        ${alert.is_resolved ? 
                            '<span class="badge bg-success ms-2">Resuelta</span>' : ''}
                        ${alert.is_acknowledged ? 
                            '<span class="badge bg-secondary ms-2">Reconocida</span>' : ''}
                    </h6>
                    <p class="mb-2">${alert.message || ''}</p>
                    <div class="alert-timestamp">
                        <i class="bi bi-clock"></i> ${formatTimestamp(alert.created_at)}
                    </div>
                </div>
                <div class="btn-group-vertical ms-3">
                    ${!alert.is_acknowledged ? `
                        <button class="btn btn-sm btn-warning" onclick="acknowledgeAlert(${alert.id})">
                            <i class="bi bi-check"></i> Reconocer
                        </button>
                    ` : ''}
                    ${!alert.is_resolved ? `
                        <button class="btn btn-sm btn-success" onclick="resolveAlert(${alert.id})">
                            <i class="bi bi-check-all"></i> Resolver
                        </button>
                    ` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

function updateAlertCount(count) {
    const badge = document.getElementById('alert-count');
    badge.textContent = count;
    badge.style.display = count > 0 ? 'inline' : 'none';
}

async function acknowledgeAlert(alertId) {
    try {
        await fetchAPI(`/alerts/${alertId}/acknowledge`, { method: 'POST' });
        showNotification('Alerta reconocida', 'success');
        loadAlerts();
    } catch (error) {
        showNotification('Error reconociendo alerta', 'error');
    }
}

async function resolveAlert(alertId) {
    try {
        await fetchAPI(`/alerts/${alertId}/resolve`, { method: 'POST' });
        showNotification('Alerta resuelta', 'success');
        loadAlerts();
        loadDashboard(); // Refresh stats
    } catch (error) {
        showNotification('Error resolviendo alerta', 'error');
    }
}

// ============================================
// MODALS SETUP
// ============================================
function setupModals() {
    // Add Device Modal
    document.getElementById('save-device-btn').addEventListener('click', async () => {
        const deviceData = {
            device_id: document.getElementById('device-id').value,
            name: document.getElementById('device-name').value,
            device_type: document.getElementById('device-type').value,
            rubro: document.getElementById('device-rubro').value,
            location: document.getElementById('device-location').value
        };
        
        try {
            await fetchAPI('/devices', {
                method: 'POST',
                body: JSON.stringify(deviceData)
            });
            
            showNotification('Dispositivo agregado exitosamente', 'success');
            bootstrap.Modal.getInstance(document.getElementById('addDeviceModal')).hide();
            document.getElementById('add-device-form').reset();
            loadDashboard();
            
        } catch (error) {
            showNotification('Error agregando dispositivo: ' + error.message, 'error');
        }
    });
    
    // Add Rule Modal
    document.getElementById('save-rule-btn').addEventListener('click', async () => {
        const ruleData = {
            name: document.getElementById('rule-name').value,
            description: document.getElementById('rule-description').value,
            condition: {
                device_id: document.getElementById('rule-device').value,
                operator: document.getElementById('rule-operator').value,
                value: parseFloat(document.getElementById('rule-value').value),
                parameter: 'value'
            },
            action: {
                type: document.getElementById('rule-action-type').value,
                severity: document.getElementById('rule-severity').value,
                message: document.getElementById('rule-message').value
            },
            is_active: true,
            priority: 5,
            cooldown_seconds: 300
        };
        
        try {
            await fetchAPI('/rules', {
                method: 'POST',
                body: JSON.stringify(ruleData)
            });
            
            showNotification('Regla creada exitosamente', 'success');
            bootstrap.Modal.getInstance(document.getElementById('addRuleModal')).hide();
            document.getElementById('add-rule-form').reset();
            loadRules();
            
        } catch (error) {
            showNotification('Error creando regla: ' + error.message, 'error');
        }
    });
    
    // Load devices in rule modal when opened
    document.getElementById('addRuleModal').addEventListener('show.bs.modal', async () => {
        const devices = await fetchAPI('/devices');
        const select = document.getElementById('rule-device');
        select.innerHTML = devices.map(d => 
            `<option value="${d.device_id}">${d.name} (${d.device_id})</option>`
        ).join('');
    });
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
async function fetchAPI(endpoint, options = {}) {
    const url = API_BASE + endpoint;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };
    
    const response = await fetch(url, config);
    
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000); // seconds
    
    if (diff < 60) return 'Hace ' + diff + 's';
    if (diff < 3600) return 'Hace ' + Math.floor(diff / 60) + 'm';
    if (diff < 86400) return 'Hace ' + Math.floor(diff / 3600) + 'h';
    
    return date.toLocaleString('es-AR');
}

function showNotification(message, type = 'info') {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'error' ? 'danger' : type} position-fixed top-0 end-0 m-3`;
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => toast.remove(), 5000);
}

function startAutoRefresh() {
    // Refresh every 5 seconds
    refreshInterval = setInterval(() => {
        if (currentSection === 'dashboard') {
            loadDashboard();
        }
    }, 5000);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
}

// ============================================
// EXPORT FOR USE IN OTHER MODULES
// ============================================
window.dashboard = {
    loadDashboard,
    loadDevices,
    loadRules,
    loadAlerts,
    showDeviceDetails,
    fetchAPI,
    showNotification
};
