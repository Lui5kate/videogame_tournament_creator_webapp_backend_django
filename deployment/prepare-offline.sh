#!/bin/bash
# Script maestro para preparar deployment offline completo

echo "🚀 PREPARANDO DEPLOYMENT OFFLINE COMPLETO"
echo "=========================================="

# 1. Descargar dependencias Python
echo "📦 1/4 - Descargando dependencias Python..."
./deployment/download-python-deps.sh

# 2. Descargar dependencias Node.js
echo "📦 2/4 - Descargando dependencias Node.js..."
./deployment/download-node-deps.sh

# 3. Crear build de producción del frontend
echo "🏗️ 3/4 - Creando build de producción..."
cd frontend
npm run build
cd ..

# 4. Copiar archivos estáticos
echo "📁 4/4 - Preparando archivos estáticos..."
mkdir -p deployment/static-files
cp -r frontend/dist/* deployment/static-files/
cp -r static/* deployment/static-files/ 2>/dev/null || true
cp -r media deployment/ 2>/dev/null || true

echo ""
echo "✅ DEPLOYMENT OFFLINE PREPARADO"
echo "================================"
echo "📦 Dependencias Python: deployment/python-deps/"
echo "📦 Dependencias Node.js: deployment/node-deps/"
echo "🏗️ Build frontend: deployment/static-files/"
echo "📁 Media files: deployment/media/"
echo ""
echo "🚀 Listo para transferir al servidor sin internet"
