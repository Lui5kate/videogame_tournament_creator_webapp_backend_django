#!/bin/bash
# Script para descargar dependencias Python offline

echo "🐍 Descargando dependencias Python para deployment offline..."

# Crear directorio para dependencias
mkdir -p deployment/python-deps

# Descargar todas las dependencias con pip download
pip download -r requirements.txt -d deployment/python-deps/

echo "✅ Dependencias Python descargadas en deployment/python-deps/"
echo "📦 Archivos .whl listos para instalación offline"

# Crear script de instalación offline
cat > deployment/install-python-deps.sh << 'EOF'
#!/bin/bash
# Instalar dependencias Python desde archivos locales
echo "📦 Instalando dependencias Python desde archivos locales..."
pip install --no-index --find-links deployment/python-deps/ -r requirements.txt
echo "✅ Dependencias Python instaladas"
EOF

chmod +x deployment/install-python-deps.sh
echo "✅ Script de instalación offline creado: deployment/install-python-deps.sh"
