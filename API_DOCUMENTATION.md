# 🎮 API Documentation - Torneo de Videojuegos

> **Base URL:** `http://localhost:8000/api/`

## 📋 Índice de Endpoints

### 🏆 Tournaments
- [GET /tournaments/](#get-tournaments) - Listar torneos
- [POST /tournaments/](#post-tournaments) - Crear torneo
- [GET /tournaments/{id}/](#get-tournamentsid) - Detalle del torneo
- [POST /tournaments/{id}/start/](#post-tournamentsidstart) - Iniciar torneo
- [GET /tournaments/{id}/stats/](#get-tournamentsidstats) - Estadísticas
- [POST /tournaments/{id}/finish/](#post-tournamentsidfinish) - Finalizar torneo

### 👥 Teams
- [GET /teams/](#get-teams) - Listar equipos
- [POST /teams/](#post-teams) - Registrar equipo
- [POST /teams/{id}/upload-photo/](#post-teamsidupload-photo) - Subir foto
- [GET /teams/{id}/players/](#get-teamsidplayers) - Jugadores del equipo

### 🎮 Games
- [GET /games/](#get-games) - Listar juegos
- [POST /games/](#post-games) - Crear juego personalizado
- [GET /games/predefined/](#get-gamespredefined) - Juegos predefinidos

### 🏅 Matches (Brackets)
- [GET /matches/](#get-matches) - Listar partidas
- [POST /matches/declare-winner/](#post-matchesdeclare-winner) - Declarar ganador
- [POST /matches/generate-brackets/](#post-matchesgenerate-brackets) - Generar brackets
- [GET /matches/visualization/](#get-matchesvisualization) - Visualización

### 💬 Chat
- [GET /messages/](#get-messages) - Mensajes del chat
- [POST /messages/](#post-messages) - Enviar mensaje
- [GET /rooms/by-tournament/](#get-roomsby-tournament) - Sala por torneo

---

## 🏆 Tournaments

### GET /tournaments/
Obtener lista de todos los torneos.

**Query Parameters:**
- Ninguno

**Response:**
```json
[
  {
    "id": 1,
    "name": "Torneo de Prueba Gaming",
    "description": "Torneo de prueba para testing",
    "tournament_type": "single",
    "status": "registration",
    "max_teams": 8,
    "points_per_win": 3,
    "points_per_participation": 1,
    "registered_teams_count": 4,
    "completed_matches_count": 0,
    "total_matches_count": 0,
    "can_start": true,
    "created_at": "2024-10-31T06:19:00Z"
  }
]
```

### POST /tournaments/
Crear un nuevo torneo.

**Request Body:**
```json
{
  "name": "Mi Torneo Gaming",
  "description": "Descripción del torneo",
  "tournament_type": "single",
  "max_teams": 16,
  "points_per_win": 3,
  "points_per_participation": 1
}
```

**Response:**
```json
{
  "id": 2,
  "name": "Mi Torneo Gaming",
  "status": "registration",
  "created_at": "2024-10-31T12:00:00Z"
}
```

### GET /tournaments/{id}/
Obtener detalles completos de un torneo específico.

**Response:**
```json
{
  "id": 1,
  "name": "Torneo de Prueba Gaming",
  "teams": [...],
  "matches": [...],
  "registered_teams_count": 4
}
```

### POST /tournaments/{id}/start/
Iniciar un torneo y generar brackets automáticamente.

**Response:**
```json
{
  "message": "Torneo iniciado exitosamente",
  "tournament": {...}
}
```

### GET /tournaments/{id}/stats/
Obtener estadísticas completas del torneo.

**Response:**
```json
{
  "tournament_info": {
    "name": "Torneo de Prueba Gaming",
    "type": "Eliminación Simple",
    "status": "En Progreso"
  },
  "teams_stats": {
    "total_teams": 4,
    "active_teams": 3,
    "eliminated_teams": 1
  },
  "matches_stats": {
    "total_matches": 3,
    "completed_matches": 1,
    "pending_matches": 2
  },
  "leaderboard": [...]
}
```

---

## 👥 Teams

### GET /teams/
Obtener lista de equipos.

**Query Parameters:**
- `tournament` - ID del torneo para filtrar

**Response:**
```json
[
  {
    "id": 1,
    "name": "Los Guerreros",
    "wins": 2,
    "losses": 0,
    "points": 8,
    "bracket_status": "winners",
    "players": [
      {
        "id": 1,
        "name": "Mario",
        "is_captain": true,
        "photo": null
      },
      {
        "id": 2,
        "name": "Luigi",
        "is_captain": false,
        "photo": null
      }
    ]
  }
]
```

### POST /teams/
Registrar un nuevo equipo con jugadores.

**Request Body:**
```json
{
  "tournament": 1,
  "name": "Nuevo Equipo",
  "players": [
    {
      "name": "Jugador 1",
      "is_captain": true
    },
    {
      "name": "Jugador 2",
      "is_captain": false
    }
  ]
}
```

### POST /teams/{id}/upload-photo/
Subir foto del equipo.

**Request:** Multipart form data
- `team_photo`: archivo de imagen

**Response:**
```json
{
  "message": "Foto subida exitosamente",
  "team_photo_url": "/media/teams/1/Nuevo_Equipo/photo.jpg"
}
```

---

## 🎮 Games

### GET /games/
Obtener lista de juegos disponibles.

**Query Parameters:**
- `type` - `predefined` o `custom`

**Response:**
```json
[
  {
    "id": 1,
    "name": "Mario Kart",
    "emoji": "🏎️",
    "display_name": "🏎️ Mario Kart",
    "is_predefined": true,
    "is_active": true
  }
]
```

### POST /games/
Crear juego personalizado.

**Request Body:**
```json
{
  "name": "Mi Juego Custom",
  "emoji": "🎯",
  "description": "Descripción del juego"
}
```

### GET /games/predefined/
Obtener juegos predefinidos disponibles.

**Response:**
```json
{
  "predefined_games": [...],
  "available_templates": {
    "games": [
      {
        "key": "mario_kart",
        "name": "Mario Kart",
        "emoji": "🏎️",
        "display_name": "🏎️ Mario Kart"
      }
    ]
  }
}
```

---

## 🏅 Matches (Brackets)

### GET /matches/
Obtener lista de partidas.

**Query Parameters:**
- `tournament` - ID del torneo
- `bracket_type` - `winners`, `losers`, `grand_final`
- `status` - `pending`, `in_progress`, `completed`

**Response:**
```json
[
  {
    "id": 1,
    "team1": {
      "id": 1,
      "name": "Los Guerreros"
    },
    "team2": {
      "id": 2,
      "name": "Team Rocket"
    },
    "winner": null,
    "bracket_type": "winners",
    "round_number": 1,
    "match_number": 1,
    "status": "pending",
    "is_ready_to_play": true
  }
]
```

### POST /matches/declare-winner/
Declarar ganador de una partida.

**Request Body:**
```json
{
  "match_id": 1,
  "winner_id": 1
}
```

**Response:**
```json
{
  "message": "Los Guerreros ha ganado la partida",
  "match": {...},
  "winner": {
    "name": "Los Guerreros",
    "points": 11,
    "wins": 3
  },
  "loser": {
    "name": "Team Rocket",
    "bracket_status": "eliminated"
  }
}
```

### POST /matches/generate-brackets/
Generar brackets para un torneo.

**Request Body:**
```json
{
  "tournament_id": 1
}
```

**Response:**
```json
{
  "message": "Brackets generados exitosamente",
  "tournament_type": "single",
  "total_matches": 3,
  "matches": [...]
}
```

### GET /matches/visualization/
Obtener datos para visualización de brackets.

**Query Parameters:**
- `tournament_id` - ID del torneo (requerido)

**Response:**
```json
{
  "tournament": {
    "id": 1,
    "name": "Torneo de Prueba Gaming",
    "type": "single",
    "status": "active"
  },
  "brackets": {
    "winners_bracket": [...],
    "losers_bracket": [...],
    "grand_final": [...]
  }
}
```

---

## 💬 Chat

### GET /messages/
Obtener mensajes del chat.

**Query Parameters:**
- `tournament` - ID del torneo
- `type` - `user`, `system`, `celebration`
- `limit` - Número máximo de mensajes (default: 100)

**Response:**
```json
[
  {
    "id": 1,
    "username": "Mario",
    "message": "¡Vamos a ganar este torneo!",
    "message_type": "user",
    "created_at": "2024-10-31T12:30:00Z",
    "formatted_time": "12:30"
  },
  {
    "id": 2,
    "username": "Sistema",
    "message": "🎉 ¡Los Guerreros ha ganado una partida! 🏆",
    "message_type": "celebration",
    "created_at": "2024-10-31T12:35:00Z"
  }
]
```

### POST /messages/
Enviar mensaje al chat.

**Request Body:**
```json
{
  "tournament": 1,
  "username": "Mario",
  "message": "¡Buena partida!"
}
```

### GET /rooms/by-tournament/
Obtener sala de chat por torneo.

**Query Parameters:**
- `tournament_id` - ID del torneo (requerido)

**Response:**
```json
{
  "chat_room": {
    "id": 1,
    "tournament": 1,
    "tournament_name": "Torneo de Prueba Gaming",
    "is_active": true,
    "recent_messages": [...],
    "message_count": 15
  },
  "created": false
}
```

---

## 🚀 Flujo de Uso Completo

### 1. Crear Torneo
```bash
POST /api/tournaments/
{
  "name": "Mi Torneo",
  "tournament_type": "single",
  "max_teams": 8
}
```

### 2. Registrar Equipos
```bash
POST /api/teams/
{
  "tournament": 1,
  "name": "Mi Equipo",
  "players": [
    {"name": "Jugador 1", "is_captain": true},
    {"name": "Jugador 2", "is_captain": false}
  ]
}
```

### 3. Iniciar Torneo
```bash
POST /api/tournaments/1/start/
```

### 4. Declarar Ganadores
```bash
POST /api/matches/declare-winner/
{
  "match_id": 1,
  "winner_id": 1
}
```

### 5. Ver Estadísticas
```bash
GET /api/tournaments/1/stats/
```

---

## 🔧 Códigos de Estado HTTP

- `200 OK` - Solicitud exitosa
- `201 Created` - Recurso creado exitosamente
- `400 Bad Request` - Error en los datos enviados
- `404 Not Found` - Recurso no encontrado
- `500 Internal Server Error` - Error del servidor

---

## 📝 Notas Importantes

1. **Archivos de Imagen:** Usar `multipart/form-data` para subir fotos
2. **Filtros:** Muchos endpoints soportan filtros por query parameters
3. **Paginación:** Los endpoints de lista pueden implementar paginación
4. **CORS:** Habilitado para desarrollo frontend
5. **Autenticación:** Actualmente no requerida (AllowAny)

---

**🎮 ¡Tu API está lista para crear torneos épicos!**
