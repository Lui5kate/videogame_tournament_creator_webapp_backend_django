#!/bin/bash

# Configuración del proyecto frontend
USUARIO_SSH="ll8202"
IP_SERVIDOR="10.150.153.31"
NOMBRE_IMAGEN_BASE="tournament_gaming_frontend"
VERSION_NUEVA="v$(date +%Y%m%d_%H%M%S)"
NOMBRE_IMAGEN_NUEVA="localhost/${USUARIO_SSH}_${NOMBRE_IMAGEN_BASE}:${VERSION_NUEVA}"
NOMBRE_TAR_NUEVA="${USUARIO_SSH}_${NOMBRE_IMAGEN_BASE}_${VERSION_NUEVA}"
DIRECTORIO_LOCAL="$(pwd)"
RUTA_DESTINO="Desarrollos/images"

# Función para manejar errores
handle_error() {
    echo "Error en línea $1. Saliendo..."
    exit 1
}

echo "===================================================="
echo "        DEPLOY FRONTEND TOURNAMENT GAMING v2.5     "
echo "===================================================="

# 1. Construir imagen frontend
echo "Paso 1: Construyendo imagen frontend..."
podman build -t "${NOMBRE_IMAGEN_NUEVA}" -f Dockerfile.frontend . || handle_error $LINENO
echo "Construcción completada."
echo "----------------------------------------------------"

# 2. Guardar imagen en tar
echo "Paso 2: Guardando imagen en archivo tar..."
podman save -o "${DIRECTORIO_LOCAL}/${NOMBRE_TAR_NUEVA}.tar" "${NOMBRE_IMAGEN_NUEVA}" || handle_error $LINENO
echo "Archivo tar guardado."
echo "----------------------------------------------------"

# 3. Enviar tar al servidor
echo "Paso 3: Enviando archivo tar al servidor..."
scp "${DIRECTORIO_LOCAL}/${NOMBRE_TAR_NUEVA}.tar" "$USUARIO_SSH@$IP_SERVIDOR:$RUTA_DESTINO/${NOMBRE_TAR_NUEVA}.tar" || handle_error $LINENO
echo "Archivo enviado."
echo "----------------------------------------------------"

# 4. Cargar imagen en servidor
echo "Paso 4: Cargando imagen en servidor..."
ssh "$USUARIO_SSH@$IP_SERVIDOR" "podman load -i $RUTA_DESTINO/${NOMBRE_TAR_NUEVA}.tar" || handle_error $LINENO

ID_IMAGEN_NUEVA=$(ssh "$USUARIO_SSH@$IP_SERVIDOR" "podman images --filter 'reference=localhost/${USUARIO_SSH}_${NOMBRE_IMAGEN_BASE}:${VERSION_NUEVA}' --format '{{.ID}}' | head -n 1 2>/dev/null")
echo "ID de imagen: $ID_IMAGEN_NUEVA"
echo "----------------------------------------------------"

# 5. Detener contenedor que use el mismo puerto
echo "Paso 5: Verificando si hay contenedores usando el puerto 8096..."
ID_CONTENEDOR_PUERTO=$(ssh "$USUARIO_SSH@$IP_SERVIDOR" "podman ps --format '{{.ID}} {{.Ports}}' | grep '8096' | awk '{print \$1}' 2>/dev/null")

if [ -z "$ID_CONTENEDOR_PUERTO" ]; then
    echo "No hay contenedores usando el puerto 8096."
else
    echo "Contenedor usando puerto 8096: $ID_CONTENEDOR_PUERTO"
    echo "Deteniendo contenedor que usa el puerto..."
    ssh "$USUARIO_SSH@$IP_SERVIDOR" "podman stop $ID_CONTENEDOR_PUERTO" || handle_error $LINENO
    echo "Contenedor detenido con éxito."
fi
echo "----------------------------------------------------"

# 6. Ejecutar nuevo contenedor frontend
echo "Paso 6: Ejecutando nuevo contenedor frontend..."
ssh "$USUARIO_SSH@$IP_SERVIDOR" "
    cd Desarrollos/images/ && \
    podman run -d --name ${NOMBRE_TAR_NUEVA} -p $IP_SERVIDOR:8096:80 ${ID_IMAGEN_NUEVA}
" || handle_error $LINENO
echo "Contenedor frontend ejecutado."
echo "----------------------------------------------------"

# 7. Verificar logs
echo "Paso 7: Verificando logs..."
sleep 10
ssh "$USUARIO_SSH@$IP_SERVIDOR" "podman logs --tail 5 ${NOMBRE_TAR_NUEVA}" || handle_error $LINENO

echo "===================================================="
echo "        FRONTEND DEPLOY COMPLETADO EXITOSAMENTE     "
echo "Frontend: http://10.150.153.31:8096"
echo "===================================================="
