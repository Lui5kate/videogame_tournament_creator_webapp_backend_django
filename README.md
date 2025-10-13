# 🎮 Torneo de Videojuegos - Backend Django v2.0

> **Aplicación web completa para gestionar torneos de videojuegos por parejas con backend Django profesional y escalable.**

## 🚀 Características Principales

### ✨ **Funcionalidades Implementadas**
- ✅ **Sistema de Torneos** - Eliminación simple y doble
- ✅ **Registro de Equipos** - Con fotos flexibles y validaciones
- ✅ **Gestión de Juegos** - Predefinidos y personalizados
- ✅ **Brackets Dinámicos** - Generación automática y seguimiento
- ✅ **Sistema de Puntuación** - 3 puntos victoria, 1 participación
- ✅ **Chat en Vivo** - Sin autenticación, mensajes del sistema
- ✅ **Clasificación Automática** - Con medallas y estadísticas

### 🏗️ **Arquitectura del Proyecto**

```
tournament_manager/
├── tournaments/     # Gestión de torneos
├── teams/          # Equipos y jugadores
├── games/          # Juegos disponibles
├── brackets/       # Partidas y brackets
├── chat/           # Chat en vivo
└── media/          # Archivos subidos
```

## 🛠️ **Stack Tecnológico**

- **Backend:** Django 4.2.7 + Django REST Framework
- **Base de Datos:** SQLite (desarrollo) / PostgreSQL (producción)
- **Archivos:** Pillow para manejo de imágenes
- **API:** REST API completa con CORS habilitado

## 📦 **Instalación y Configuración**

### **1. Clonar y Configurar Entorno**
```bash
git clone <repository-url>
cd v2-backend_django
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### **2. Instalar Dependencias**
```bash
pip install -r requirements.txt
```

### **3. Configurar Base de Datos**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Opcional
```

### **4. Ejecutar Servidor**
```bash
python manage.py runserver
```

## 📊 **Modelos de Datos**

### **Tournament (Torneo)**
- Nombre, descripción, tipo (simple/doble eliminación)
- Estado (configuración, registro, activo, finalizado)
- Configuración de puntos y límites

### **Team (Equipo)**
- Nombre único por torneo
- Foto de equipo o jugadores individuales
- Estadísticas (victorias, derrotas, puntos)
- Estado en bracket (winners/losers/eliminado/campeón)

### **Player (Jugador)**
- Nombre y foto individual
- Relación con equipo
- Indicador de capitán

### **Game (Juego)**
- Juegos predefinidos con emojis
- Juegos personalizados con imágenes
- Asignación a torneos específicos

### **Match (Partida)**
- Equipos participantes y ganador
- Tipo de bracket (winners/losers/gran final)
- Ronda y número de partida
- Timestamps de inicio y finalización

### **ChatMessage (Mensaje)**
- Usuario simple sin autenticación
- Mensajes de usuario y del sistema
- Celebraciones automáticas

## 🎯 **API Endpoints (Planificados)**

```
GET  /api/tournaments/              # Listar torneos
POST /api/tournaments/              # Crear torneo
GET  /api/tournaments/{id}/         # Detalle torneo
POST /api/tournaments/{id}/start/   # Iniciar torneo

GET  /api/teams/                    # Listar equipos
POST /api/teams/                    # Registrar equipo
POST /api/teams/{id}/upload-photo/  # Subir foto

GET  /api/games/                    # Listar juegos
POST /api/games/                    # Crear juego personalizado

GET  /api/brackets/{tournament_id}/ # Ver brackets
POST /api/brackets/declare-winner/  # Declarar ganador

GET  /api/chat/{tournament_id}/     # Mensajes del chat
POST /api/chat/{tournament_id}/     # Enviar mensaje
```

## 🎨 **Sistema de Diseño Arcade**

### **Paleta de Colores**
- **Primario:** `#ff6b35` (Naranja gaming)
- **Secundario:** `#f7931e` (Amarillo retro)
- **Acento:** `#ffcc02` (Amarillo brillante)
- **Fondo:** `#1a1a2e` (Azul oscuro)

### **Tipografía**
- **Principal:** "Press Start 2P" (Pixel gaming)
- **Secundaria:** Sans-serif moderna (legibilidad)

## 🚀 **Flujo de Uso**

### **1. Configuración del Torneo**
1. Crear torneo con tipo de eliminación
2. Configurar juegos disponibles
3. Abrir registro de equipos

### **2. Registro de Equipos**
1. Equipos se registran con nombres de jugadores
2. Subir fotos (equipo completo o individuales)
3. Validación automática de datos

### **3. Inicio del Torneo**
1. Generar brackets automáticamente
2. Asignar juegos a partidas
3. Activar chat en vivo

### **4. Gestión de Partidas**
1. Seguimiento en tiempo real
2. Declarar ganadores
3. Actualización automática de clasificación
4. Mensajes de celebración en chat

### **5. Finalización**
1. Determinar campeón
2. Clasificación final con medallas
3. Historial completo del torneo

## 🔧 **Próximas Funcionalidades**

- [ ] **Frontend React/Vue** - Interfaz de usuario completa
- [ ] **WebSockets** - Chat en tiempo real
- [ ] **Notificaciones** - Alertas de partidas
- [ ] **Estadísticas Avanzadas** - Gráficos y métricas
- [ ] **Exportación** - PDF de resultados
- [ ] **Multi-torneo** - Gestión simultánea
- [ ] **Autenticación** - Sistema de usuarios opcional

## 📱 **Compatibilidad**

- **Navegadores:** Chrome, Firefox, Safari, Edge
- **Dispositivos:** Responsive design mobile-first
- **Offline:** Funcionalidad básica sin conexión

## 🎮 **Casos de Uso**

- **Eventos Gaming** - Cumpleaños y celebraciones
- **Competencias Locales** - Torneos comunitarios
- **Gaming Cafés** - Eventos regulares
- **Escuelas/Universidades** - Competencias estudiantiles

---

**Desarrollado con ❤️ para la comunidad gaming**
