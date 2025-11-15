# 🧪 Tests - Tournament Gaming App

## Estructura de Pruebas

```
tests/
├── README.md              # Este archivo
├── general_tests.sh       # Pruebas generales del sistema
└── stress-tests/
    └── stress_test.sh     # Pruebas de estrés y rendimiento
```

## 🔍 Pruebas Generales

Verifican el funcionamiento básico del sistema:

```bash
# Ejecutar pruebas generales
chmod +x tests/general_tests.sh
./tests/general_tests.sh
```

**Incluye:**
- ✅ Conectividad frontend/backend
- ✅ Endpoints principales del API
- ✅ Rutas SPA del frontend
- ✅ Estado de contenedores
- ✅ Conexión a base de datos
- ✅ Tiempos de respuesta básicos

## 🔥 Pruebas de Estrés

Evalúan el rendimiento bajo carga:

```bash
# Ejecutar pruebas de estrés
chmod +x tests/stress-tests/stress_test.sh
./tests/stress-tests/stress_test.sh
```

**Incluye:**
- 🔥 Frontend: 50 requests concurrentes
- 🔥 Frontend: 200 requests concurrentes  
- 🔥 Backend: 100 requests API
- 🔥 Backend: Múltiples endpoints
- 🔥 Prueba de resistencia: 5 minutos

## 📊 Interpretación de Resultados

### Códigos de Estado Esperados:
- **200**: OK (frontend)
- **401**: No autorizado (backend sin token)
- **404**: No encontrado (rutas inexistentes)

### Tiempos Aceptables:
- **Frontend**: < 1 segundo
- **Backend**: < 0.5 segundos
- **Bajo carga**: < 2 segundos

## 🚀 Uso Rápido

```bash
# Prueba rápida del sistema
./tests/general_tests.sh

# Prueba de rendimiento completa
./tests/stress-tests/stress_test.sh

# Solo verificar conectividad
curl -I http://10.150.153.31:8096
curl -I http://10.150.153.31:8097/api/games/
```

## 📝 Logs

Los logs de las pruebas de estrés se guardan temporalmente en `/tmp/`:
- `frontend_*.log`
- `backend_*.log` 
- `endurance.log`
