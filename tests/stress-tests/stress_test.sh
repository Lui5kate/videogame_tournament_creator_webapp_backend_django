#!/bin/bash

# =============================================================================
# PRUEBAS DE ESTRÉS - TOURNAMENT GAMING APP
# =============================================================================

FRONTEND_URL="http://10.150.153.31:8096"
BACKEND_URL="http://10.150.153.31:8097/api"

echo "======================================================"
echo "           PRUEBAS DE ESTRÉS - TOURNAMENT GAMING      "
echo "======================================================"
echo "Frontend: $FRONTEND_URL"
echo "Backend:  $BACKEND_URL"
echo "======================================================"

# Función para calcular estadísticas
calculate_stats() {
    local file=$1
    echo "📊 Estadísticas:"
    echo "   Total requests: $(wc -l < $file)"
    echo "   Exitosos (200): $(grep -c "200" $file)"
    echo "   Errores (4xx/5xx): $(grep -c -E "(4[0-9][0-9]|5[0-9][0-9])" $file)"
    echo "   Tiempo promedio: $(awk '{sum+=$2} END {printf "%.3fs\n", sum/NR}' $file)"
    echo "   Tiempo mínimo: $(sort -k2 -n $file | head -1 | awk '{print $2}')"
    echo "   Tiempo máximo: $(sort -k2 -n $file | tail -1 | awk '{print $2}')"
}

# Test 1: Frontend - Carga ligera
echo "🔥 Test 1: Frontend - Carga ligera (50 requests)"
for i in {1..50}; do 
    curl -s -o /dev/null -w "%{http_code} %{time_total}\n" $FRONTEND_URL/ & 
done
wait > /tmp/frontend_light.log 2>/dev/null
calculate_stats /tmp/frontend_light.log
echo ""

# Test 2: Frontend - Carga pesada  
echo "🔥 Test 2: Frontend - Carga pesada (200 requests)"
for i in {1..200}; do 
    curl -s -o /dev/null -w "%{http_code} %{time_total}\n" $FRONTEND_URL/ & 
done
wait > /tmp/frontend_heavy.log 2>/dev/null
calculate_stats /tmp/frontend_heavy.log
echo ""

# Test 3: Backend - API endpoints
echo "🔥 Test 3: Backend - API endpoints (100 requests)"
for i in {1..100}; do 
    curl -s -o /dev/null -w "%{http_code} %{time_total}\n" $BACKEND_URL/games/ & 
done
wait > /tmp/backend_api.log 2>/dev/null
calculate_stats /tmp/backend_api.log
echo ""

# Test 4: Backend - Múltiples endpoints
echo "🔥 Test 4: Backend - Múltiples endpoints (50 cada uno)"
endpoints=("games" "tournaments" "teams" "matches")
for endpoint in "${endpoints[@]}"; do
    echo "   Testing /$endpoint/..."
    for i in {1..50}; do 
        curl -s -o /dev/null -w "%{http_code} %{time_total}\n" $BACKEND_URL/$endpoint/ & 
    done
    wait > /tmp/backend_$endpoint.log 2>/dev/null
    calculate_stats /tmp/backend_$endpoint.log
done
echo ""

# Test 5: Prueba de resistencia (5 minutos)
echo "🔥 Test 5: Prueba de resistencia (5 minutos)"
echo "   Enviando 1 request cada 2 segundos..."
start_time=$(date +%s)
end_time=$((start_time + 300)) # 5 minutos
count=0

while [ $(date +%s) -lt $end_time ]; do
    curl -s -o /dev/null -w "%{http_code} %{time_total}\n" $FRONTEND_URL/ >> /tmp/endurance.log &
    curl -s -o /dev/null -w "%{http_code} %{time_total}\n" $BACKEND_URL/games/ >> /tmp/endurance.log &
    sleep 2
    count=$((count + 2))
    echo -ne "   Requests enviados: $count\r"
done
wait
echo ""
calculate_stats /tmp/endurance.log
echo ""

# Resumen final
echo "======================================================"
echo "           RESUMEN DE PRUEBAS COMPLETADO             "
echo "======================================================"
echo "✅ Todas las pruebas completadas"
echo "📁 Logs guardados en /tmp/"
echo "🔍 Para ver detalles: cat /tmp/frontend_*.log"
echo "======================================================"

# Limpiar archivos temporales
# rm -f /tmp/frontend_*.log /tmp/backend_*.log /tmp/endurance.log
