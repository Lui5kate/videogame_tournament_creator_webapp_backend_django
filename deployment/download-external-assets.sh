#!/bin/bash
# Script para descargar recursos externos para deployment offline

echo "🌐 Descargando recursos externos para deployment offline..."

# Crear directorios
mkdir -p deployment/external-assets/fonts
mkdir -p deployment/external-assets/css

# URLs de Google Fonts que se usan en el proyecto
GOOGLE_FONTS_URLS=(
    "https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap"
    "https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Orbitron:wght@400;700;900&display=swap"
)

echo "📥 Descargando Google Fonts CSS..."

# Descargar CSS de Google Fonts
for i in "${!GOOGLE_FONTS_URLS[@]}"; do
    url="${GOOGLE_FONTS_URLS[$i]}"
    filename="google-fonts-$((i+1)).css"
    
    echo "  - Descargando: $filename"
    curl -s "$url" > "deployment/external-assets/css/$filename"
    
    # Extraer URLs de fuentes del CSS y descargarlas
    echo "  - Extrayendo URLs de fuentes..."
    grep -o 'https://fonts.gstatic.com/[^)]*' "deployment/external-assets/css/$filename" | while read font_url; do
        font_filename=$(basename "$font_url")
        echo "    - Descargando fuente: $font_filename"
        curl -s "$font_url" > "deployment/external-assets/fonts/$font_filename"
    done
done

# Crear CSS local que reemplace las URLs externas
echo "🔧 Creando CSS local..."

cat > deployment/external-assets/css/local-fonts.css << 'EOF'
/* Press Start 2P Font - Local */
@font-face {
  font-family: 'Press Start 2P';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('../fonts/e3t4euO8T-267oIAQAu6jDQyK0nSgPJE4580.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}

/* Orbitron Font - Local */
@font-face {
  font-family: 'Orbitron';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('../fonts/yMJMMIlzdpvBhQQL_SC3X9yhF25-T1nyGy6BoWgz.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}

@font-face {
  font-family: 'Orbitron';
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url('../fonts/yMJMMIlzdpvBhQQL_SC3X9yhF25-T1nyGy6BoWgz.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}

@font-face {
  font-family: 'Orbitron';
  font-style: normal;
  font-weight: 900;
  font-display: swap;
  src: url('../fonts/yMJMMIlzdpvBhQQL_SC3X9yhF25-T1nyGy6BoWgz.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
EOF

# Crear versiones offline de los archivos HTML y CSS
echo "📝 Creando versiones offline..."

# Backup del index.html original
cp frontend/index.html frontend/index.html.backup

# Crear index.html offline
cat > deployment/external-assets/index-offline.html << 'EOF'
<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>🎮 Videogame Tourney Maker</title>
    <!-- Local fonts instead of Google Fonts -->
    <link rel="stylesheet" href="/assets/css/local-fonts.css">
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
EOF

# Backup del index.css original
cp frontend/src/index.css frontend/src/index.css.backup

# Crear index.css offline
cat > deployment/external-assets/index-offline.css << 'EOF'
/* Local font import instead of Google Fonts */
/* @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap'); */

@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-dark text-white font-gaming;
  }
}

/* Rest of the CSS remains the same... */
EOF

# Copiar el resto del CSS original (sin la línea de Google Fonts)
tail -n +3 frontend/src/index.css >> deployment/external-assets/index-offline.css

echo ""
echo "✅ RECURSOS EXTERNOS DESCARGADOS"
echo "================================="
echo "📁 Fuentes: deployment/external-assets/fonts/"
echo "📁 CSS: deployment/external-assets/css/"
echo "📄 HTML offline: deployment/external-assets/index-offline.html"
echo "📄 CSS offline: deployment/external-assets/index-offline.css"
echo ""
echo "🔧 Para usar offline:"
echo "1. Copiar fuentes a frontend/public/assets/fonts/"
echo "2. Copiar CSS local a frontend/public/assets/css/"
echo "3. Reemplazar index.html con la versión offline"
echo "4. Reemplazar src/index.css con la versión offline"
