#!/bin/bash
# Script de deployment completo

echo "🚀 INICIANDO DEPLOYMENT COMPLETO"
echo "================================="

# 1. Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado"
    exit 1
fi

# 2. Configurar variables de entorno
if [ ! -f ".env" ]; then
    echo "📝 Copiando variables de entorno..."
    cp .env.production .env
    echo "⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales reales"
    read -p "Presiona Enter cuando hayas editado .env..."
fi

# 3. Construir imágenes
echo "🏗️  Construyendo imágenes Docker..."
docker-compose build

# 4. Iniciar servicios
echo "🚀 Iniciando servicios..."
docker-compose up -d

# 5. Esperar a que MySQL esté listo
echo "⏳ Esperando a que MySQL esté listo..."
sleep 30

# 6. Ejecutar migraciones
echo "📊 Ejecutando migraciones..."
docker-compose exec backend python manage.py migrate

# 7. Crear superusuario (opcional)
echo "👤 ¿Crear superusuario? (y/n)"
read -r create_superuser
if [ "$create_superuser" = "y" ]; then
    docker-compose exec backend python manage.py createsuperuser
fi

# 8. Poblar datos iniciales
echo "🎮 Poblando juegos predefinidos..."
docker-compose exec backend python manage.py shell -c "
from games.models import Game
Game.create_predefined_games()
print('✅ Juegos predefinidos creados')
"

echo ""
echo "✅ DEPLOYMENT COMPLETADO"
echo "========================"
echo "🌐 Frontend: http://localhost"
echo "🔧 Backend API: http://localhost/api/"
echo "📊 Admin: http://localhost/admin/"
echo ""
echo "📋 Comandos útiles:"
echo "docker-compose logs -f          # Ver logs"
echo "docker-compose stop             # Detener"
echo "docker-compose restart          # Reiniciar"
echo "docker-compose down             # Eliminar contenedores"
