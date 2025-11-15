#!/bin/bash
# Script de deployment para Podman

echo "🚀 DEPLOYMENT CON PODMAN"
echo "========================"

# Verificar Podman
if ! command -v podman &> /dev/null; then
    echo "❌ Podman no está instalado"
    exit 1
fi

if ! command -v podman-compose &> /dev/null; then
    echo "❌ Podman-compose no está instalado"
    exit 1
fi

# Configurar variables de entorno
if [ ! -f ".env" ]; then
    cp .env.production .env
    echo "⚠️  Edita .env con tus credenciales"
    read -p "Presiona Enter cuando hayas editado .env..."
fi

# Construir con Podman
echo "🏗️  Construyendo con Podman..."
podman-compose build

# Iniciar servicios
echo "🚀 Iniciando servicios..."
podman-compose up -d

# Esperar MySQL
echo "⏳ Esperando MySQL..."
sleep 30

# Migraciones
echo "📊 Ejecutando migraciones..."
podman-compose exec backend python manage.py migrate

echo ""
echo "✅ DEPLOYMENT COMPLETADO"
echo "========================"
echo "🌐 Frontend: http://10.150.153.31:8096"
echo "🔧 Backend: http://10.150.153.31:8097/api/"
echo "🗄️  MySQL: 10.150.153.31:8098"
