#!/bin/bash
# Script para aplicar configuración offline al frontend

echo "🔧 Aplicando configuración offline al frontend..."

# Crear directorios necesarios en frontend
mkdir -p frontend/public/assets/fonts
mkdir -p frontend/public/assets/css

# Copiar fuentes descargadas
echo "📁 Copiando fuentes locales..."
cp deployment/external-assets/fonts/* frontend/public/assets/fonts/

# Copiar CSS local
echo "📁 Copiando CSS local..."
cp deployment/external-assets/css/local-fonts.css frontend/public/assets/css/

# Aplicar HTML offline
echo "📄 Aplicando HTML offline..."
cp deployment/external-assets/index-offline.html frontend/index.html

# Aplicar CSS offline
echo "📄 Aplicando CSS offline..."
cp deployment/external-assets/index-offline.css frontend/src/index.css

echo ""
echo "✅ CONFIGURACIÓN OFFLINE APLICADA"
echo "================================="
echo "✅ Fuentes copiadas a frontend/public/assets/fonts/"
echo "✅ CSS local copiado a frontend/public/assets/css/"
echo "✅ HTML actualizado para usar recursos locales"
echo "✅ CSS actualizado sin dependencias externas"
echo ""
echo "🚀 El frontend ahora funciona completamente offline"
