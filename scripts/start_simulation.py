#!/usr/bin/env python3
"""
IoT Multi-Rubro System - Startup Script
========================================
Initializes and starts the complete system in simulation mode.
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend_api"))

def print_banner():
    """Print startup banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║          IoT Multi-Rubro Automation System                ║
    ║          =====================================             ║
    ║                                                           ║
    ║          🔄 Modo Simulación Activado                      ║
    ║          Sistema de automatización completo               ║
    ║          para múltiples rubros comerciales                ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if required dependencies are installed."""
    print("📦 Verificando dependencias...")
    
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import numpy
        print("  ✓ Todas las dependencias están instaladas")
        return True
    except ImportError as e:
        print(f"  ✗ Falta dependencia: {e.name}")
        print("\n  Instale las dependencias con:")
        print("  pip install -r backend_api/requirements.txt")
        return False

def initialize_database():
    """Initialize database with realistic demo data."""
    print("\n🗄️  Inicializando base de datos con datos realistas...")
    
    try:
        from database import init_database
        
        init_database()
        print("  ✓ Schema de base de datos creado")
        
        # Try to load realistic seed data
        try:
            import seed_realistic_data
            seed_realistic_data.seed_realistic_data()
            print("  ✓ Datos realistas cargados (7 días históricos)")
        except Exception as seed_error:
            print(f"  ⚠ Error cargando datos realistas, usando datos básicos: {seed_error}")
            from database import seed_demo_data
            seed_demo_data()
        
        return True
    except Exception as e:
        print(f"  ✗ Error inicializando base de datos: {e}")
        return False

def start_backend():
    """Start FastAPI backend server."""
    print("\n🚀 Iniciando servidor backend...")
    
    backend_dir = Path(__file__).parent.parent / "backend_api"
    
    # Start server in background
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=str(backend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("  ✓ Servidor backend iniciado (PID: {})".format(process.pid))
        print("  📡 API: http://localhost:8000")
        print("  📚 Docs: http://localhost:8000/docs")
        
        return process
    except Exception as e:
        print(f"  ✗ Error iniciando servidor: {e}")
        return None

def wait_for_server(max_attempts=30):
    """Wait for backend server to be ready."""
    print("\n⏳ Esperando que el servidor esté listo...")
    
    import urllib.request
    import urllib.error
    
    for attempt in range(max_attempts):
        try:
            urllib.request.urlopen("http://localhost:8000/health", timeout=1)
            print("  ✓ Servidor listo!")
            return True
        except (urllib.error.URLError, Exception):
            time.sleep(1)
            print(f"  ... intento {attempt + 1}/{max_attempts}", end='\r')
    
    print("  ✗ Timeout esperando al servidor")
    return False

def open_dashboard():
    """Open dashboard in default browser."""
    print("\n🌐 Abriendo dashboard...")
    
    try:
        webbrowser.open("http://localhost:8000")
        print("  ✓ Dashboard abierto en el navegador")
        return True
    except Exception as e:
        print(f"  ✗ No se pudo abrir el navegador: {e}")
        print("  Abra manualmente: http://localhost:8000")
        return False

def print_usage_info():
    """Print usage information."""
    info = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                   SISTEMA INICIADO                        ║
    ╚═══════════════════════════════════════════════════════════╝
    
    🎯 Accesos:
       • Dashboard: http://localhost:8000
       • API Docs:  http://localhost:8000/docs
       • Health:    http://localhost:8000/health
    
    👤 Credenciales Demo:
       • Usuario: admin
       • Contraseña: admin123
    
    📊 Dispositivos simulados:
       • TEMP-001: Freezer de Carnicería
       • HUM-001:  Sensor de Humedad
       • MOT-001:  Contador de Personas
       • SOIL-001: Sensor de Humedad de Suelo
    
    🔧 Funcionalidades:
       ✓ Monitoreo en tiempo real (WebSocket)
       ✓ Reglas de automatización
       ✓ Sistema de alertas
       ✓ Gráficos interactivos
       ✓ Gestión de dispositivos
    
    ⚙️  Configuración:
       Para cambiar a modo hardware, edite:
       backend_api/config.py → SIM_MODE = False
    
    🛑 Para detener el sistema:
       Presione Ctrl+C
    
    ═══════════════════════════════════════════════════════════
    """
    print(info)

def cleanup(process):
    """Cleanup on exit."""
    print("\n\n🛑 Deteniendo sistema...")
    
    if process:
        process.terminate()
        try:
            process.wait(timeout=5)
            print("  ✓ Servidor detenido")
        except subprocess.TimeoutExpired:
            process.kill()
            print("  ✓ Servidor forzado a detener")

def main():
    """Main startup sequence."""
    backend_process = None
    
    try:
        print_banner()
        
        # Check dependencies
        if not check_dependencies():
            sys.exit(1)
        
        # Initialize database
        if not initialize_database():
            sys.exit(1)
        
        # Start backend
        backend_process = start_backend()
        if not backend_process:
            sys.exit(1)
        
        # Wait for server
        if not wait_for_server():
            cleanup(backend_process)
            sys.exit(1)
        
        # Open dashboard
        open_dashboard()
        
        # Print usage info
        print_usage_info()
        
        # Keep running
        print("💚 Sistema ejecutándose. Presione Ctrl+C para detener.\n")
        
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupción detectada...")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
    finally:
        cleanup(backend_process)
        print("\n✓ Sistema detenido correctamente")

if __name__ == "__main__":
    main()
