#!/bin/bash

# Script para descargar dependencias Python offline
echo "🐍 Descargando dependencias Python para deployment offline..."

# Crear directorio para dependencias
mkdir -p offline-deps/backend

# Descargar todas las dependencias con sus subdependencias
pip download -r requirements-production.txt -d offline-deps/backend/

echo "✅ Dependencias Python descargadas en: offline-deps/backend/"
echo "📦 Archivos .whl listos para instalación offline"

# Crear script de instalación offline
cat > offline-deps/backend/install-offline.sh << 'EOF'
#!/bin/bash
echo "📦 Instalando dependencias Python desde archivos offline..."
pip install --no-index --find-links . -r ../requirements-production.txt
echo "✅ Instalación offline completada"
EOF

chmod +x offline-deps/backend/install-offline.sh
echo "🚀 Script de instalación offline creado"
