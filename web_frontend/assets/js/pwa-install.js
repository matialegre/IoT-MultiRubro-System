/**
 * PWA Installation Handler
 * ========================
 * Gestiona la instalación de la PWA y muestra prompts personalizados
 */

class PWAInstaller {
    constructor() {
        this.deferredPrompt = null;
        this.init();
    }

    init() {
        // Registrar Service Worker
        if ('serviceWorker' in navigator) {
            this.registerServiceWorker();
        }

        // Detectar evento de instalación
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallPrompt();
        });

        // Detectar instalación exitosa
        window.addEventListener('appinstalled', () => {
            console.log('✅ PWA instalada correctamente');
            this.deferredPrompt = null;
            this.hideInstallPrompt();
            
            if (typeof notify !== 'undefined') {
                notify.success('¡Instalado!', 'La app se instaló correctamente en tu dispositivo');
            }
        });

        // Detectar si ya está instalado
        if (window.matchMedia('(display-mode: standalone)').matches) {
            console.log('✅ PWA ejecutándose en modo standalone');
            document.body.classList.add('pwa-installed');
        }

        // Mostrar banner iOS si es iPhone/iPad
        this.detectiOS();
    }

    async registerServiceWorker() {
        try {
            const registration = await navigator.serviceWorker.register('/service-worker.js');
            console.log('✅ Service Worker registrado:', registration.scope);

            // Actualizar service worker automáticamente
            registration.addEventListener('updatefound', () => {
                const newWorker = registration.installing;
                newWorker.addEventListener('statechange', () => {
                    if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                        console.log('🔄 Nueva versión disponible');
                        this.showUpdateAvailable();
                    }
                });
            });
        } catch (error) {
            console.error('❌ Error registrando Service Worker:', error);
        }
    }

    showInstallPrompt() {
        // Crear banner de instalación personalizado
        const banner = document.createElement('div');
        banner.id = 'pwa-install-banner';
        banner.className = 'pwa-install-banner';
        banner.innerHTML = `
            <style>
                .pwa-install-banner {
                    position: fixed;
                    bottom: 20px;
                    left: 50%;
                    transform: translateX(-50%);
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 16px 24px;
                    border-radius: 16px;
                    box-shadow: 0 8px 24px rgba(0,0,0,0.2);
                    z-index: 10000;
                    max-width: 90%;
                    width: 400px;
                    animation: slideUp 0.3s ease;
                }
                
                @keyframes slideUp {
                    from {
                        transform: translateX(-50%) translateY(100px);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(-50%) translateY(0);
                        opacity: 1;
                    }
                }
                
                .pwa-install-banner h4 {
                    margin: 0 0 8px 0;
                    font-size: 1.1rem;
                }
                
                .pwa-install-banner p {
                    margin: 0 0 16px 0;
                    font-size: 0.9rem;
                    opacity: 0.95;
                }
                
                .pwa-install-actions {
                    display: flex;
                    gap: 12px;
                }
                
                .pwa-install-actions button {
                    flex: 1;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 8px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s;
                }
                
                .btn-install {
                    background: white;
                    color: #667eea;
                }
                
                .btn-install:hover {
                    transform: scale(1.05);
                }
                
                .btn-later {
                    background: rgba(255,255,255,0.2);
                    color: white;
                }
            </style>
            <h4>📱 Instalar IoT System</h4>
            <p>Accede más rápido y usa la app offline</p>
            <div class="pwa-install-actions">
                <button class="btn-install" onclick="pwaInstaller.install()">
                    Instalar
                </button>
                <button class="btn-later" onclick="pwaInstaller.hideInstallPrompt()">
                    Más tarde
                </button>
            </div>
        `;

        document.body.appendChild(banner);
    }

    hideInstallPrompt() {
        const banner = document.getElementById('pwa-install-banner');
        if (banner) {
            banner.style.animation = 'slideDown 0.3s ease';
            setTimeout(() => banner.remove(), 300);
        }
    }

    async install() {
        if (!this.deferredPrompt) {
            console.log('⚠️ Prompt de instalación no disponible');
            return;
        }

        this.deferredPrompt.prompt();
        const { outcome } = await this.deferredPrompt.userChoice;
        
        console.log(`Usuario eligió: ${outcome}`);
        this.deferredPrompt = null;
        this.hideInstallPrompt();
    }

    showUpdateAvailable() {
        if (typeof notify !== 'undefined') {
            notify.info(
                'Actualización disponible',
                'Nueva versión de la app disponible',
                {
                    duration: 0,
                    actions: [
                        {
                            label: 'Actualizar',
                            style: 'primary',
                            onClick: 'location.reload()'
                        }
                    ]
                }
            );
        }
    }

    detectiOS() {
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        const isInStandaloneMode = window.navigator.standalone === true;

        if (isIOS && !isInStandaloneMode) {
            // Mostrar instrucciones específicas para iOS
            setTimeout(() => {
                this.showiOSInstructions();
            }, 3000);
        }
    }

    showiOSInstructions() {
        // Verificar si ya se mostró (usar localStorage)
        if (localStorage.getItem('ios-instructions-shown')) {
            return;
        }

        const banner = document.createElement('div');
        banner.id = 'ios-install-banner';
        banner.className = 'ios-install-banner';
        banner.innerHTML = `
            <style>
                .ios-install-banner {
                    position: fixed;
                    bottom: 20px;
                    left: 50%;
                    transform: translateX(-50%);
                    background: white;
                    color: #1f2937;
                    padding: 20px;
                    border-radius: 16px;
                    box-shadow: 0 8px 24px rgba(0,0,0,0.2);
                    z-index: 10000;
                    max-width: 90%;
                    width: 380px;
                    animation: slideUp 0.3s ease;
                }
                
                .ios-install-banner h4 {
                    margin: 0 0 12px 0;
                    font-size: 1.1rem;
                    color: #667eea;
                }
                
                .ios-steps {
                    margin: 16px 0;
                }
                
                .ios-step {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    margin-bottom: 12px;
                    font-size: 0.9rem;
                }
                
                .ios-step-icon {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: 700;
                    flex-shrink: 0;
                }
                
                .ios-actions {
                    text-align: center;
                    margin-top: 16px;
                }
                
                .ios-actions button {
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 10px 24px;
                    border-radius: 8px;
                    font-weight: 600;
                    cursor: pointer;
                }
            </style>
            <h4>📱 Instalar en iPhone/iPad</h4>
            <div class="ios-steps">
                <div class="ios-step">
                    <div class="ios-step-icon">1</div>
                    <div>Toca el botón <strong>Compartir</strong> ⬆️ abajo</div>
                </div>
                <div class="ios-step">
                    <div class="ios-step-icon">2</div>
                    <div>Selecciona <strong>"Agregar a pantalla de inicio"</strong></div>
                </div>
                <div class="ios-step">
                    <div class="ios-step-icon">3</div>
                    <div>Toca <strong>"Agregar"</strong> arriba a la derecha</div>
                </div>
            </div>
            <div class="ios-actions">
                <button onclick="pwaInstaller.hideiOSInstructions()">
                    Entendido
                </button>
            </div>
        `;

        document.body.appendChild(banner);
        localStorage.setItem('ios-instructions-shown', 'true');
    }

    hideiOSInstructions() {
        const banner = document.getElementById('ios-install-banner');
        if (banner) {
            banner.style.animation = 'slideDown 0.3s ease';
            setTimeout(() => banner.remove(), 300);
        }
    }
}

// Inicializar automáticamente
const pwaInstaller = new PWAInstaller();

// Exponer globalmente
window.pwaInstaller = pwaInstaller;

console.log('✅ PWA Installer inicializado');
