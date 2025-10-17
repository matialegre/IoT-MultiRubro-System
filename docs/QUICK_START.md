# 🚀 Guía de Inicio Rápido

## Instalación en 3 Pasos

### 1️⃣ Instalar Dependencias

```bash
# Navegar al directorio del proyecto
cd IoT-MultiRubro-System

# Instalar dependencias de Python
cd backend_api
pip install -r requirements.txt
```

**Dependencias principales:**
- Python 3.11+
- FastAPI
- SQLAlchemy
- NumPy
- Uvicorn

### 2️⃣ Iniciar el Sistema

**Opción A: Script Automático (Recomendado)**

```bash
# Windows
python scripts\start_simulation.py

# Linux/Mac
python3 scripts/start_simulation.py
```

**Opción B: Manual**

```bash
cd backend_api
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3️⃣ Acceder al Dashboard

Abrir navegador en: **http://localhost:8000**

**Credenciales:**
- Usuario: `admin`
- Contraseña: `admin123`

---

## 📊 Primeros Pasos

### Ver Dashboard

El dashboard muestra:
- ✅ Dispositivos conectados en tiempo real
- 📈 Gráficos de sensores actualizados automáticamente
- ⚠️ Alertas activas del sistema
- 📊 Estadísticas generales

### Dispositivos Demo Pre-configurados

| ID | Nombre | Tipo | Rubro |
|----|--------|------|-------|
| TEMP-001 | Freezer Principal | Temperatura | Carnicería |
| HUM-001 | Sensor Humedad | Humedad | Carnicería |
| MOT-001 | Contador Personas | Movimiento | Tienda Ropa |
| SOIL-001 | Humedad Suelo | Soil Moisture | Riego |

### Agregar Nuevo Dispositivo

1. Click en **"Dispositivos"** en el menú
2. Click en **"Agregar Dispositivo"**
3. Completar formulario:
   - **ID:** Identificador único (ej: TEMP-002)
   - **Nombre:** Nombre descriptivo
   - **Tipo:** Seleccionar tipo de sensor
   - **Rubro:** Sector comercial
   - **Ubicación:** Ubicación física

4. Click **"Guardar"**

### Crear Regla de Automatización

1. Ir a sección **"Reglas"**
2. Click en **"Crear Regla"**
3. Configurar condición:
   ```
   SI temperatura > 25°C
   ENTONCES generar alerta crítica
   ```
4. Establecer acción deseada
5. Click **"Crear Regla"**

**Ejemplo de Regla JSON:**
```json
{
  "name": "Temperatura Alta",
  "condition": {
    "device_id": "TEMP-001",
    "operator": ">",
    "value": 25
  },
  "action": {
    "type": "alert",
    "severity": "critical",
    "message": "Temperatura excede límite: {value}°C"
  }
}
```

---

## 🔧 Configuración

### Cambiar Modo de Operación

Editar `backend_api/config.py`:

```python
# MODO SIMULACIÓN (sin hardware)
SIM_MODE = True

# MODO HARDWARE (ESP32 real)
SIM_MODE = False
```

### Configurar Base de Datos

**SQLite (Simulación - Por defecto):**
```python
DATABASE_URL = "sqlite:///./iot_multirubro.db"
```

**SQL Server (Producción):**
```python
DATABASE_URL = "mssql+pyodbc://user:pass@server/database?driver=ODBC+Driver+17+for+SQL+Server"
```

### Ajustar Tasa de Actualización

En `config.py`:
```python
SIMULATOR_UPDATE_RATE = 1.0  # Segundos entre lecturas
```

---

## 📡 API REST

### Endpoints Principales

**Dispositivos:**
```bash
# Listar todos
GET http://localhost:8000/api/devices

# Crear nuevo
POST http://localhost:8000/api/devices
Content-Type: application/json

{
  "device_id": "TEMP-002",
  "name": "Sensor Nuevo",
  "device_type": "temperature",
  "rubro": "carniceria"
}
```

**Datos de Sensores:**
```bash
# Obtener histórico
GET http://localhost:8000/api/data/TEMP-001?hours=24&limit=100

# Enviar dato manualmente
POST http://localhost:8000/api/data
{
  "device_id": "TEMP-001",
  "value": 22.5,
  "unit": "°C"
}
```

**Reglas:**
```bash
# Listar reglas activas
GET http://localhost:8000/api/rules?active_only=true

# Crear regla
POST http://localhost:8000/api/rules
```

**Alertas:**
```bash
# Ver alertas sin resolver
GET http://localhost:8000/api/alerts?unresolved_only=true

# Reconocer alerta
POST http://localhost:8000/api/alerts/1/acknowledge

# Resolver alerta
POST http://localhost:8000/api/alerts/1/resolve
```

### WebSocket en Tiempo Real

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/realtime');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Datos en tiempo real:', data);
};
```

---

## 🧪 Verificar Instalación

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "mode": "simulation",
  "timestamp": "2025-01-17T03:33:00Z"
}
```

### Test 2: Listar Dispositivos
```bash
curl http://localhost:8000/api/devices
```

### Test 3: Estadísticas
```bash
curl http://localhost:8000/api/stats
```

---

## 🐛 Solución de Problemas

### Error: "Module not found"
```bash
pip install -r backend_api/requirements.txt
```

### Error: "Port 8000 already in use"
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux
lsof -ti:8000 | xargs kill -9
```

### Error: "Database locked"
```bash
# Eliminar base de datos y reiniciar
rm backend_api/iot_multirubro.db
python scripts/start_simulation.py
```

### Dashboard no actualiza datos
1. Verificar WebSocket en consola del navegador (F12)
2. Verificar que el servidor esté corriendo
3. Refrescar página (Ctrl+F5)

---

## 📚 Documentación Adicional

- **[API Reference](API_REFERENCE.md)** - Referencia completa de la API
- **[Architecture](ARCHITECTURE.md)** - Arquitectura del sistema
- **[Sensor Models](SENSOR_MODELS.md)** - Modelos físicos de sensores
- **[ESP32 Firmware](../iot_firmware/README.md)** - Configuración de hardware

---

## 🎯 Siguientes Pasos

1. ✅ **Explorar Dashboard** - Familiarizarse con la interfaz
2. ✅ **Crear Reglas** - Automatizar respuestas a eventos
3. ✅ **Probar Alertas** - Simular condiciones críticas
4. ✅ **Integrar Hardware** - Conectar ESP32 real (modo hardware)
5. ✅ **Personalizar** - Adaptar al rubro específico

---

## 💡 Casos de Uso por Rubro

### 🥩 Carnicería/Panadería
```python
# Monitoreo de temperatura de cámaras frigoríficas
# Alertas de excursión térmica
# Registro histórico para trazabilidad
```

### 👕 Tienda de Ropa
```python
# Contador de personas
# Control automático de iluminación
# Análisis de flujo por horario
```

### 🌱 Riego
```python
# Humedad de suelo
# Activación automática de válvulas
# Programación horaria
```

### 🍺 Bar/Boliche
```python
# Sistema de tarjetas RFID/QR
# Control de stock
# Reportes de ventas
```

---

## 🆘 Soporte

- **GitHub Issues:** [Reportar problema](https://github.com/your-repo/issues)
- **Documentación:** Ver carpeta `/docs`
- **Email:** support@iot-multirubro.local

---

**¡Sistema listo para usar! 🚀**
