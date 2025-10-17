@echo off
chcp 65001 >nul
color 0A
cls

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║        🚀 SISTEMA IoT MULTI-RUBRO - INICIO AUTOMÁTICO       ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Verificar que Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python no está instalado o no está en el PATH
    echo.
    echo Por favor instala Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python detectado
echo.

REM Cambiar al directorio del proyecto
cd /d "%~dp0"
echo 📂 Directorio del proyecto: %cd%
echo.

REM Verificar si existe la base de datos
if not exist "backend_api\iot_system.db" (
    echo 🔧 Primera vez - Inicializando base de datos...
    echo.
    
    REM Instalar dependencias si no existen
    if not exist "backend_api\venv\" (
        echo 📦 Instalando dependencias...
        cd backend_api
        pip install -r requirements.txt
        cd ..
        echo.
    )
    
    REM Inicializar base de datos IoT
    echo 🗄️  Creando base de datos IoT...
    python backend_api\database.py
    echo.
    
    REM Cargar datos realistas
    echo 📊 Cargando datos realistas (7 días de históricos)...
    python backend_api\seed_realistic_data.py
    echo.
    
    REM Inicializar CRM
    echo 💼 Inicializando CRM y sistema de demos...
    python backend_api\init_crm_db.py
    echo.
)

echo ═══════════════════════════════════════════════════════════════
echo.
echo 🚀 INICIANDO SERVIDOR...
echo.
echo 📱 Accesos disponibles:
echo.
echo   💻 Escritorio:   http://localhost:8000
echo   📱 Celular:      http://TU_IP_LOCAL:8000
echo   📊 API Docs:     http://localhost:8000/docs
echo   🎯 Demo:         http://localhost:8000/demo.html
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo 📱 PARA INSTALAR EN iPHONE:
echo.
echo   1. Abre Safari en tu iPhone
echo   2. Ve a: http://TU_IP_LOCAL:8000
echo   3. Toca el botón "Compartir" (⬆️)
echo   4. Selecciona "Agregar a pantalla de inicio"
echo   5. ¡Listo! Ya tienes la app instalada
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo ⚠️  IMPORTANTE: Para obtener tu IP local ejecuta: ipconfig
echo     Busca "IPv4" (ejemplo: 192.168.1.100)
echo.
echo 🛑 Para detener el servidor: Presiona Ctrl+C
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

REM Obtener IP local automáticamente
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    goto :found_ip
)
:found_ip
set IP=%IP:~1%

if not "%IP%"=="" (
    echo 🌐 Tu IP local es: %IP%
    echo.
    echo    Accede desde tu celular en: http://%IP%:8000
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo.
)

REM Iniciar servidor en modo simulación
cd backend_api
echo 🟢 Servidor iniciando...
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

REM Si el servidor se detiene
echo.
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo 🛑 Servidor detenido
echo.
pause
