# 🎮 Sistema de Diseño - Torneo de Videojuegos

## Objetivo Principal

Crear web app de un creador de torneos de videojuegos donde puedas crear, seguimiento, personalización de torneos de videojuegos profesionales donde su sistema de torneo es muy similar a start.gg y que sea visualizable los brackets del torneo, torneo de eliminación simple y doble, donde guarde en una base de datos los elementos del torneo, estado del torneo, equipos, clasificaciones, chat, etc

## Elementos a Extraer y Estructurar

### 1. Paleta de Colores Gaming

- **Colores arcade específicos** por componente (brackets, equipos, clasificación, chat)
- **Gradientes retro** con direcciones y puntos de color exactos del tema gaming
- **Variaciones por estado** de torneo (activo, completado, próximo, ganador)
- **Colores de feedback** para victorias, derrotas y empates

### 2. Tipografía Pixel Perfect

- **Fuente "Press Start 2P"** con tamaños por jerarquía (títulos de sección, nombres de equipos, puntuaciones)
- **Fuentes de respaldo** para legibilidad en móviles
- **Espaciado retro** entre líneas y caracteres
- **Colores de texto** por contexto gaming (ganadores, perdedores, neutro)

### 3. Componentes Gaming

- **Tarjetas de equipos** con fotos y estadísticas
- **Brackets interactivos** con conexiones visuales
- **Botones arcade** con efectos hover gaming
- **Tabla de clasificación** con medallas y posiciones
- **Chat gaming** con burbujas de mensaje retro

### 4. Layout Arcade

- **Espaciado** entre elementos del torneo
- **Patrones de distribución** para brackets y clasificaciones
- **Sistema responsive** mobile-first para eventos
- **Grids específicos** para equipos y partidas

## Formato JSON

```json
{
  "colores_arcade": {
    "primarios": { 
      "naranja_gaming": "#ff6b35", 
      "amarillo_retro": "#f7931e",
      "azul_acento": "#ffcc02"
    },
    "estados_torneo": {
      "ganador": "#00ff00",
      "perdedor": "#ff4444", 
      "activo": "#ffcc02",
      "completado": "#888888"
    },
    "componentes": {
      "brackets": { "fondo": "#hex", "conexiones": "#hex" },
      "equipos": { "tarjeta": "#hex", "borde_activo": "#hex" },
      "clasificacion": { "podium": "#hex", "posiciones": "#hex" },
      "chat": { "burbuja": "#hex", "timestamp": "#hex" }
    }
  },
  "tipografia_gaming": {
    "pixel_title": { 
      "font": "Press Start 2P", 
      "size": "24px", 
      "weight": "400",
      "uso": "títulos principales"
    },
    "pixel_subtitle": { 
      "font": "Press Start 2P", 
      "size": "16px", 
      "weight": "400",
      "uso": "nombres de equipos"
    },
    "legible_body": { 
      "font": "Arial", 
      "size": "14px", 
      "weight": "400",
      "uso": "estadísticas y chat"
    }
  },
  "efectos_arcade": {
    "sombras_gaming": {
      "tarjeta_equipo": "0 4px 8px rgba(255, 107, 53, 0.3)",
      "boton_hover": "0 0 20px rgba(255, 204, 2, 0.6)",
      "bracket_activo": "0 0 15px rgba(247, 147, 30, 0.5)"
    },
    "bordes_pixel": {
      "radius": "8px",
      "style": "solid 2px",
      "hover_glow": "0 0 10px currentColor"
    },
    "transiciones": {
      "hover_scale": "transform: scale(1.05)",
      "duration": "200ms",
      "easing": "ease-out"
    }
  },
  "espaciado_torneo": {
    "equipos_grid": {
      "gap": "20px",
      "padding": "16px",
      "margin": "12px 0"
    },
    "brackets_layout": {
      "conexion_gap": "40px",
      "nivel_spacing": "80px",
      "partida_padding": "12px"
    },
    "clasificacion_table": {
      "row_height": "60px",
      "column_gap": "16px",
      "medal_size": "32px"
    }
  },
  "componentes_gaming": {
    "tarjeta_equipo": {
      "estructura": "foto + nombres + estadísticas",
      "hover": "elevación + glow naranja",
      "estado_activo": "borde amarillo pulsante"
    },
    "bracket_conexion": {
      "linea_style": "2px solid #f7931e",
      "animacion": "pulso en partida activa",
      "ganador_highlight": "grosor 4px + color dorado"
    },
    "boton_arcade": {
      "base": "gradiente naranja-amarillo",
      "hover": "glow + scale",
      "active": "inset shadow + color shift"
    }
  },
  "restricciones": [
    "No aplicar efectos glow a texto pequeño",
    "No usar colores de ganador en elementos neutros",
    "Mantener contraste mínimo 4.5:1 para accesibilidad",
    "No sobrecargar con más de 3 efectos simultáneos",
    "Preservar legibilidad en dispositivos móviles"
  ],
  "responsive": {
    "mobile": "Stack vertical, botones táctiles 44px mín",
    "tablet": "Grid 2 columnas, navegación horizontal",
    "desktop": "Layout completo, efectos hover completos"
  }
}
```

## Directrices de Implementación

- **Objetivo:** Crear una guía precisa para replicar la experiencia arcade retro sin perder funcionalidad
- **Enfoque:** Patrones visuales gaming reutilizables que mantengan la identidad del torneo
- **Prioridad:** Legibilidad y usabilidad por encima de efectos decorativos
- **Consistencia:** Aplicar el tema arcade de manera uniforme en todas las secciones
- **Funcionalidades** Crear backend funcional con todas las especificaciones dadas
