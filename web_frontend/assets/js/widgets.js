/**
 * IoT Multi-Rubro - Widgets Avanzados
 * ===================================
 * Componentes interactivos para dashboard profesional
 */

class DashboardWidgets {
    constructor() {
        this.widgets = new Map();
        this.refreshIntervals = new Map();
    }

    // ============================================
    // WIDGET: REAL-TIME CLOCK
    // ============================================
    createRealtimeClock(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const widget = document.createElement('div');
        widget.className = 'widget-clock glass';
        widget.innerHTML = `
            <div class="clock-display">
                <div class="clock-time" id="clock-time">--:--:--</div>
                <div class="clock-date" id="clock-date">-- de -----, 2025</div>
                <div class="clock-timezone">Argentina (UTC-3)</div>
            </div>
            <style>
                .widget-clock {
                    padding: 20px;
                    border-radius: 16px;
                    text-align: center;
                    background: rgba(255,255,255,0.95);
                    backdrop-filter: blur(20px);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }
                .clock-time {
                    font-size: 2.5rem;
                    font-weight: 800;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 10px;
                }
                .clock-date {
                    font-size: 1rem;
                    color: #6b7280;
                    font-weight: 600;
                }
                .clock-timezone {
                    font-size: 0.8rem;
                    color: #9ca3af;
                    margin-top: 5px;
                }
            </style>
        `;

        container.appendChild(widget);

        // Update clock every second
        const updateClock = () => {
            const now = new Date();
            document.getElementById('clock-time').textContent = now.toLocaleTimeString('es-AR');
            document.getElementById('clock-date').textContent = now.toLocaleDateString('es-AR', {
                day: 'numeric',
                month: 'long',
                year: 'numeric'
            });
        };

        updateClock();
        setInterval(updateClock, 1000);

        this.widgets.set('clock', widget);
    }

    // ============================================
    // WIDGET: SYSTEM STATUS
    // ============================================
    createSystemStatus(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const widget = document.createElement('div');
        widget.className = 'widget-system-status';
        widget.innerHTML = `
            <div class="status-grid">
                <div class="status-item">
                    <div class="status-icon">🖥️</div>
                    <div class="status-label">CPU</div>
                    <div class="status-value" id="cpu-usage">--</div>
                </div>
                <div class="status-item">
                    <div class="status-icon">💾</div>
                    <div class="status-label">Memoria</div>
                    <div class="status-value" id="memory-usage">--</div>
                </div>
                <div class="status-item">
                    <div class="status-icon">🌐</div>
                    <div class="status-label">Red</div>
                    <div class="status-value" id="network-status">--</div>
                </div>
                <div class="status-item">
                    <div class="status-icon">⚡</div>
                    <div class="status-label">Uptime</div>
                    <div class="status-value" id="system-uptime">--</div>
                </div>
            </div>
            <style>
                .status-grid {
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 15px;
                }
                .status-item {
                    text-align: center;
                    padding: 15px;
                    background: rgba(255,255,255,0.95);
                    border-radius: 12px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                }
                .status-icon {
                    font-size: 2rem;
                    margin-bottom: 8px;
                }
                .status-label {
                    font-size: 0.85rem;
                    color: #6b7280;
                    font-weight: 600;
                    margin-bottom: 5px;
                }
                .status-value {
                    font-size: 1.1rem;
                    font-weight: 700;
                    color: #10b981;
                }
            </style>
        `;

        container.appendChild(widget);

        // Simulate system metrics
        this.updateSystemMetrics();
        setInterval(() => this.updateSystemMetrics(), 3000);

        this.widgets.set('systemStatus', widget);
    }

    updateSystemMetrics() {
        // Simulated metrics
        document.getElementById('cpu-usage').textContent = `${Math.floor(Math.random() * 30 + 10)}%`;
        document.getElementById('memory-usage').textContent = `${Math.floor(Math.random() * 20 + 40)}%`;
        document.getElementById('network-status').textContent = '✓ OK';
        
        // Calculate uptime
        const uptimeHours = Math.floor(performance.now() / 3600000);
        document.getElementById('system-uptime').textContent = `${uptimeHours}h`;
    }

    // ============================================
    // WIDGET: QUICK ACTIONS
    // ============================================
    createQuickActions(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const widget = document.createElement('div');
        widget.className = 'widget-quick-actions';
        widget.innerHTML = `
            <div class="quick-actions-grid">
                <button class="quick-action-btn" onclick="widgets.exportData()">
                    <i class="bi bi-download"></i>
                    <span>Exportar Datos</span>
                </button>
                <button class="quick-action-btn" onclick="widgets.generateReport()">
                    <i class="bi bi-file-earmark-text"></i>
                    <span>Generar Reporte</span>
                </button>
                <button class="quick-action-btn" onclick="widgets.refreshDashboard()">
                    <i class="bi bi-arrow-clockwise"></i>
                    <span>Actualizar</span>
                </button>
                <button class="quick-action-btn" onclick="widgets.openSettings()">
                    <i class="bi bi-gear"></i>
                    <span>Configuración</span>
                </button>
            </div>
            <style>
                .quick-actions-grid {
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 12px;
                }
                .quick-action-btn {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 8px;
                    padding: 16px;
                    background: white;
                    border: 2px solid #e5e7eb;
                    border-radius: 12px;
                    cursor: pointer;
                    transition: all 0.3s;
                    font-weight: 600;
                    color: #4b5563;
                }
                .quick-action-btn:hover {
                    border-color: #667eea;
                    color: #667eea;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
                }
                .quick-action-btn i {
                    font-size: 1.5rem;
                }
                .quick-action-btn span {
                    font-size: 0.85rem;
                }
            </style>
        `;

        container.appendChild(widget);
        this.widgets.set('quickActions', widget);
    }

    // ============================================
    // WIDGET: ACTIVITY FEED
    // ============================================
    createActivityFeed(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const widget = document.createElement('div');
        widget.className = 'widget-activity-feed glass';
        widget.innerHTML = `
            <div class="feed-header">
                <h4>Actividad Reciente</h4>
                <button class="btn-clear-feed" onclick="widgets.clearActivityFeed()">Limpiar</button>
            </div>
            <div class="feed-items" id="activity-feed-items">
                <div class="feed-empty">No hay actividad reciente</div>
            </div>
            <style>
                .widget-activity-feed {
                    background: rgba(255,255,255,0.95);
                    border-radius: 16px;
                    padding: 20px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    max-height: 400px;
                    overflow-y: auto;
                }
                .feed-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                }
                .feed-header h4 {
                    font-size: 1.1rem;
                    font-weight: 700;
                    margin: 0;
                }
                .btn-clear-feed {
                    background: none;
                    border: none;
                    color: #ef4444;
                    font-size: 0.85rem;
                    cursor: pointer;
                    font-weight: 600;
                }
                .feed-items {
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                }
                .feed-item {
                    padding: 12px;
                    background: #f9fafb;
                    border-radius: 8px;
                    border-left: 3px solid;
                    font-size: 0.9rem;
                    animation: slideInRight 0.3s ease;
                }
                .feed-item.success { border-left-color: #10b981; }
                .feed-item.warning { border-left-color: #f59e0b; }
                .feed-item.error { border-left-color: #ef4444; }
                .feed-item.info { border-left-color: #3b82f6; }
                .feed-item-time {
                    font-size: 0.75rem;
                    color: #9ca3af;
                    margin-top: 4px;
                }
                .feed-empty {
                    text-align: center;
                    color: #9ca3af;
                    padding: 20px;
                }
            </style>
        `;

        container.appendChild(widget);
        this.widgets.set('activityFeed', widget);
    }

    addActivityItem(message, type = 'info') {
        const feedItems = document.getElementById('activity-feed-items');
        if (!feedItems) return;

        // Remove empty message
        const empty = feedItems.querySelector('.feed-empty');
        if (empty) empty.remove();

        const item = document.createElement('div');
        item.className = `feed-item ${type}`;
        item.innerHTML = `
            ${message}
            <div class="feed-item-time">${new Date().toLocaleTimeString('es-AR')}</div>
        `;

        feedItems.insertBefore(item, feedItems.firstChild);

        // Limit to 20 items
        while (feedItems.children.length > 20) {
            feedItems.removeChild(feedItems.lastChild);
        }
    }

    clearActivityFeed() {
        const feedItems = document.getElementById('activity-feed-items');
        if (!feedItems) return;

        feedItems.innerHTML = '<div class="feed-empty">No hay actividad reciente</div>';
    }

    // ============================================
    // WIDGET: WEATHER (Simulado)
    // ============================================
    createWeatherWidget(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const widget = document.createElement('div');
        widget.className = 'widget-weather glass';
        widget.innerHTML = `
            <div class="weather-display">
                <div class="weather-icon">🌤️</div>
                <div class="weather-temp">24°C</div>
                <div class="weather-desc">Parcialmente nublado</div>
                <div class="weather-details">
                    <span>💧 68%</span>
                    <span>💨 15 km/h</span>
                </div>
                <div class="weather-location">Buenos Aires, AR</div>
            </div>
            <style>
                .widget-weather {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border-radius: 16px;
                    padding: 20px;
                    text-align: center;
                }
                .weather-icon {
                    font-size: 3rem;
                    margin-bottom: 10px;
                }
                .weather-temp {
                    font-size: 2.5rem;
                    font-weight: 800;
                    margin-bottom: 5px;
                }
                .weather-desc {
                    font-size: 1rem;
                    opacity: 0.9;
                    margin-bottom: 15px;
                }
                .weather-details {
                    display: flex;
                    justify-content: center;
                    gap: 20px;
                    margin-bottom: 10px;
                    font-size: 0.9rem;
                }
                .weather-location {
                    font-size: 0.85rem;
                    opacity: 0.8;
                }
            </style>
        `;

        container.appendChild(widget);
        this.widgets.set('weather', widget);
    }

    // ============================================
    // ACTION HANDLERS
    // ============================================
    async exportData() {
        notify.info('Exportando Datos', 'Preparando archivo de exportación...');
        
        // Simulate export
        setTimeout(() => {
            notify.success('Exportación Completa', 'Los datos se han descargado exitosamente');
            this.addActivityItem('📥 Datos exportados a CSV', 'success');
        }, 2000);
    }

    async generateReport() {
        notify.info('Generando Reporte', 'Creando reporte PDF...');
        
        try {
            const response = await fetch('/api/reports/daily');
            const data = await response.json();
            
            notify.success('Reporte Generado', 'El reporte está listo para descargar');
            this.addActivityItem('📄 Reporte diario generado', 'success');
        } catch (error) {
            notify.error('Error', 'No se pudo generar el reporte');
        }
    }

    refreshDashboard() {
        notify.info('Actualizando', 'Refrescando datos del dashboard...');
        
        if (window.dashboard) {
            window.dashboard.loadDashboard();
        }
        
        setTimeout(() => {
            notify.success('Actualizado', 'Dashboard refrescado correctamente');
            this.addActivityItem('🔄 Dashboard actualizado', 'info');
        }, 1000);
    }

    openSettings() {
        notify.info('Configuración', 'Abriendo panel de configuración...');
        this.addActivityItem('⚙️ Configuración accedida', 'info');
        
        // En producción, abrir modal de configuración
    }

    // ============================================
    // INITIALIZE ALL WIDGETS
    // ============================================
    initializeAll() {
        console.log('🎨 Inicializando widgets avanzados...');
        
        // Aquí se inicializarían todos los widgets
        // En producción, los contenedores estarían en el HTML
        
        console.log('✓ Widgets listos');
    }
}

// Initialize global instance
window.widgets = new DashboardWidgets();

// Auto-initialize after DOM loads
document.addEventListener('DOMContentLoaded', () => {
    window.widgets.initializeAll();
});
