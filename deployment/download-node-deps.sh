#!/bin/bash
# Script para descargar dependencias Node.js offline

echo "📦 Descargando dependencias Node.js para deployment offline..."

# Ir al directorio frontend
cd frontend

# Crear directorio para dependencias offline
mkdir -p ../deployment/node-deps

# Descargar todas las dependencias con npm pack
echo "📥 Empaquetando dependencias npm..."
npm pack --pack-destination ../deployment/node-deps/

# Crear archivo de dependencias offline
npm list --json > ../deployment/package-list.json

# Crear script de instalación offline
cat > ../deployment/install-node-deps.sh << 'EOF'
#!/bin/bash
# Instalar dependencias Node.js desde archivos locales
echo "📦 Instalando dependencias Node.js desde archivos locales..."
cd frontend
npm ci --offline --cache ../deployment/node-deps/
echo "✅ Dependencias Node.js instaladas"
EOF

chmod +x ../deployment/install-node-deps.sh

echo "✅ Dependencias Node.js descargadas en deployment/node-deps/"
echo "✅ Script de instalación offline creado: deployment/install-node-deps.sh"

cd ..
