#!/bin/bash

# =============================================================================
# PRUEBAS GENERALES - TOURNAMENT GAMING APP
# =============================================================================

FRONTEND_URL="http://10.150.153.31:8096"
BACKEND_URL="http://10.150.153.31:8097/api"

echo "======================================================"
echo "           PRUEBAS GENERALES - TOURNAMENT GAMING      "
echo "======================================================"

# Test 1: Conectividad básica
echo "🔍 Test 1: Conectividad básica"
echo -n "   Frontend: "
if curl -s -o /dev/null -w "%{http_code}" $FRONTEND_URL/ | grep -q "200"; then
    echo "✅ OK"
else
    echo "❌ FALLO"
fi

echo -n "   Backend:  "
if curl -s -o /dev/null -w "%{http_code}" $BACKEND_URL/ | grep -q -E "(200|404)"; then
    echo "✅ OK"
else
    echo "❌ FALLO"
fi
echo ""

# Test 2: Endpoints principales del API
echo "🔍 Test 2: Endpoints principales del API"
endpoints=("games" "tournaments" "teams" "matches" "messages" "rooms")
for endpoint in "${endpoints[@]}"; do
    echo -n "   /$endpoint/: "
    status=$(curl -s -o /dev/null -w "%{http_code}" $BACKEND_URL/$endpoint/)
    if [[ "$status" == "200" || "$status" == "401" ]]; then
        echo "✅ OK ($status)"
    else
        echo "❌ FALLO ($status)"
    fi
done
echo ""

# Test 3: Rutas del frontend (SPA)
echo "🔍 Test 3: Rutas del frontend (SPA)"
routes=("" "login" "register" "tournaments" "dashboard")
for route in "${routes[@]}"; do
    echo -n "   /$route: "
    if curl -s -o /dev/null -w "%{http_code}" $FRONTEND_URL/$route | grep -q "200"; then
        echo "✅ OK"
    else
        echo "❌ FALLO"
    fi
done
echo ""

# Test 4: Contenedores activos
echo "🔍 Test 4: Estado de contenedores"
echo -n "   Backend container: "
if ssh ll8202@10.150.153.31 "podman ps | grep -q tournament_gaming.*Up"; then
    echo "✅ ACTIVO"
else
    echo "❌ INACTIVO"
fi

echo -n "   Frontend container: "
if ssh ll8202@10.150.153.31 "podman ps | grep -q tournament_gaming_frontend.*Up"; then
    echo "✅ ACTIVO"
else
    echo "❌ INACTIVO"
fi
echo ""

# Test 5: Base de datos
echo "🔍 Test 5: Conexión a base de datos"
echo -n "   MySQL connection: "
if ssh ll8202@10.150.153.31 "podman exec ll8202_tournament_gaming_v* python manage.py shell -c 'from django.db import connection; connection.ensure_connection(); print(\"OK\")' 2>/dev/null | grep -q OK"; then
    echo "✅ OK"
else
    echo "❌ FALLO"
fi

echo -n "   Games table: "
game_count=$(ssh ll8202@10.150.153.31 "podman exec ll8202_tournament_gaming_v* python manage.py shell -c 'from games.models import Game; print(Game.objects.count())' 2>/dev/null")
if [[ "$game_count" -gt 0 ]]; then
    echo "✅ OK ($game_count juegos)"
else
    echo "❌ VACÍA"
fi
echo ""

# Test 6: Tiempos de respuesta
echo "🔍 Test 6: Tiempos de respuesta"
echo -n "   Frontend: "
frontend_time=$(curl -s -o /dev/null -w "%{time_total}" $FRONTEND_URL/)
echo "${frontend_time}s"

echo -n "   Backend:  "
backend_time=$(curl -s -o /dev/null -w "%{time_total}" $BACKEND_URL/games/)
echo "${backend_time}s"
echo ""

echo "======================================================"
echo "           PRUEBAS GENERALES COMPLETADAS             "
echo "======================================================"
echo "🚀 Para pruebas de estrés: ./tests/stress-tests/stress_test.sh"
echo "======================================================"
