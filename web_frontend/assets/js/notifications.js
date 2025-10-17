/**
 * IoT Multi-Rubro - Sistema de Notificaciones Real
 * ==================================================
 * Sistema completo de notificaciones toast con sonidos y persistencia
 */

class NotificationSystem {
    constructor() {
        this.notifications = [];
        this.maxNotifications = 5;
        this.soundEnabled = true;
        this.init();
    }

    init() {
        // Crear contenedor de notificaciones
        this.createContainer();
        
        // Cargar preferencias del usuario
        this.loadPreferences();
        
        // Verificar soporte de notificaciones del navegador
        this.checkBrowserSupport();
    }

    createContainer() {
        if (document.getElementById('notification-container')) return;
        
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'notification-container';
        container.innerHTML = `
            <style>
                .notification-container {
                    position: fixed;
                    top: 80px;
                    right: 20px;
                    z-index: 9999;
                    max-width: 400px;
                }
                
                .notification-toast {
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    margin-bottom: 15px;
                    padding: 16px;
                    border-left: 5px solid;
                    animation: slideInRight 0.3s ease;
                    position: relative;
                    overflow: hidden;
                }
                
                @keyframes slideInRight {
                    from {
                        transform: translateX(400px);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                
                @keyframes slideOutRight {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(400px);
                        opacity: 0;
                    }
                }
                
                .notification-toast.removing {
                    animation: slideOutRight 0.3s ease forwards;
                }
                
                .notification-toast.success {
                    border-left-color: #10b981;
                }
                
                .notification-toast.error {
                    border-left-color: #ef4444;
                }
                
                .notification-toast.warning {
                    border-left-color: #f59e0b;
                }
                
                .notification-toast.info {
                    border-left-color: #3b82f6;
                }
                
                .notification-header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 8px;
                }
                
                .notification-title {
                    font-weight: 700;
                    font-size: 0.95rem;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                
                .notification-icon {
                    font-size: 1.2rem;
                }
                
                .notification-close {
                    background: none;
                    border: none;
                    font-size: 1.3rem;
                    cursor: pointer;
                    opacity: 0.5;
                    transition: opacity 0.2s;
                    padding: 0;
                    width: 24px;
                    height: 24px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .notification-close:hover {
                    opacity: 1;
                }
                
                .notification-body {
                    font-size: 0.9rem;
                    color: #4b5563;
                    margin-bottom: 8px;
                }
                
                .notification-time {
                    font-size: 0.75rem;
                    color: #9ca3af;
                }
                
                .notification-progress {
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    height: 3px;
                    background: currentColor;
                    opacity: 0.3;
                    animation: progressBar linear forwards;
                }
                
                @keyframes progressBar {
                    from { width: 100%; }
                    to { width: 0%; }
                }
                
                .notification-actions {
                    display: flex;
                    gap: 10px;
                    margin-top: 12px;
                }
                
                .notification-action-btn {
                    padding: 6px 12px;
                    border: none;
                    border-radius: 6px;
                    font-size: 0.85rem;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s;
                }
                
                .notification-action-btn.primary {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                
                .notification-action-btn.secondary {
                    background: #f3f4f6;
                    color: #4b5563;
                }
                
                .notification-action-btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                }
            </style>
        `;
        document.body.appendChild(container);
    }

    show(options) {
        const {
            title = 'Notificación',
            message = '',
            type = 'info',
            duration = 5000,
            actions = [],
            sound = true,
            persist = false
        } = options;

        // Limitar número de notificaciones visibles
        if (this.notifications.length >= this.maxNotifications) {
            this.notifications[0].remove();
        }

        const id = `notif-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const notification = this.createNotification(id, title, message, type, duration, actions, persist);
        
        const container = document.getElementById('notification-container');
        container.appendChild(notification);
        
        this.notifications.push(notification);

        // Reproducir sonido
        if (sound && this.soundEnabled) {
            this.playSound(type);
        }

        // Auto-remover después de duration
        if (!persist && duration > 0) {
            setTimeout(() => {
                this.remove(id);
            }, duration);
        }

        return id;
    }

    createNotification(id, title, message, type, duration, actions, persist) {
        const notif = document.createElement('div');
        notif.id = id;
        notif.className = `notification-toast ${type}`;
        
        const icon = this.getIcon(type);
        
        notif.innerHTML = `
            <div class="notification-header">
                <div class="notification-title">
                    <span class="notification-icon">${icon}</span>
                    ${title}
                </div>
                <button class="notification-close" onclick="window.notificationSystem.remove('${id}')">&times;</button>
            </div>
            ${message ? `<div class="notification-body">${message}</div>` : ''}
            <div class="notification-time">${this.getTimeString()}</div>
            ${actions.length > 0 ? this.createActions(actions, id) : ''}
            ${!persist && duration > 0 ? `<div class="notification-progress" style="animation-duration: ${duration}ms;"></div>` : ''}
        `;
        
        return notif;
    }

    createActions(actions, notifId) {
        const actionsHtml = actions.map(action => `
            <button class="notification-action-btn ${action.style || 'secondary'}" 
                    onclick="${action.onClick}; window.notificationSystem.remove('${notifId}');">
                ${action.label}
            </button>
        `).join('');
        
        return `<div class="notification-actions">${actionsHtml}</div>`;
    }

    getIcon(type) {
        const icons = {
            success: '✓',
            error: '✗',
            warning: '⚠',
            info: 'ℹ'
        };
        return icons[type] || icons.info;
    }

    getTimeString() {
        return new Date().toLocaleTimeString('es-AR', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }

    remove(id) {
        const notif = document.getElementById(id);
        if (!notif) return;

        notif.classList.add('removing');
        
        setTimeout(() => {
            notif.remove();
            this.notifications = this.notifications.filter(n => n.id !== id);
        }, 300);
    }

    success(title, message, options = {}) {
        return this.show({ title, message, type: 'success', ...options });
    }

    error(title, message, options = {}) {
        return this.show({ title, message, type: 'error', duration: 7000, ...options });
    }

    warning(title, message, options = {}) {
        return this.show({ title, message, type: 'warning', duration: 6000, ...options });
    }

    info(title, message, options = {}) {
        return this.show({ title, message, type: 'info', ...options });
    }

    playSound(type) {
        // [Simulación] En producción, usar audio real
        const sounds = {
            success: 440, // Hz
            error: 200,
            warning: 300,
            info: 500
        };
        
        // Usar Web Audio API para sonidos sutiles
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = sounds[type] || sounds.info;
            gainNode.gain.value = 0.1; // Volumen bajo
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.1);
        } catch (e) {
            // Silenciar errores de audio
        }
    }

    checkBrowserSupport() {
        if ('Notification' in window && Notification.permission === 'default') {
            // Mostrar notificación para solicitar permiso
            setTimeout(() => {
                this.info(
                    'Notificaciones',
                    'Habilita las notificaciones del navegador para recibir alertas',
                    {
                        actions: [
                            {
                                label: 'Habilitar',
                                style: 'primary',
                                onClick: 'window.notificationSystem.requestPermission()'
                            }
                        ],
                        persist: false,
                        duration: 10000
                    }
                );
            }, 2000);
        }
    }

    requestPermission() {
        if ('Notification' in window) {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    this.success('¡Listo!', 'Notificaciones habilitadas correctamente');
                }
            });
        }
    }

    sendBrowserNotification(title, message, icon = '/favicon.ico') {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: icon,
                badge: icon,
                tag: 'iot-system',
                requireInteraction: false
            });
        }
    }

    loadPreferences() {
        try {
            const prefs = JSON.parse(localStorage.getItem('notificationPrefs') || '{}');
            this.soundEnabled = prefs.soundEnabled !== false;
        } catch (e) {
            // Usar valores por defecto
        }
    }

    savePreferences() {
        localStorage.setItem('notificationPrefs', JSON.stringify({
            soundEnabled: this.soundEnabled
        }));
    }

    toggleSound() {
        this.soundEnabled = !this.soundEnabled;
        this.savePreferences();
        
        this.info(
            'Sonido',
            `Sonido de notificaciones ${this.soundEnabled ? 'activado' : 'desactivado'}`
        );
    }

    clearAll() {
        this.notifications.forEach(notif => {
            this.remove(notif.id);
        });
    }
}

// Inicializar sistema global
window.notificationSystem = new NotificationSystem();

// Alias para facilitar uso
window.notify = {
    success: (title, msg, opts) => window.notificationSystem.success(title, msg, opts),
    error: (title, msg, opts) => window.notificationSystem.error(title, msg, opts),
    warning: (title, msg, opts) => window.notificationSystem.warning(title, msg, opts),
    info: (title, msg, opts) => window.notificationSystem.info(title, msg, opts)
};

console.log('✓ Sistema de notificaciones inicializado');
