#!/bin/bash

# Configuración del proyecto
USUARIO_SSH="ll8202"
IP_SERVIDOR="10.150.153.31"
NOMBRE_IMAGEN_BASE="tournament_gaming"
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
echo "           DEPLOY TOURNAMENT GAMING v2.5           "
echo "===================================================="

# 1. Verificar si la imagen ya existe en local y construir si no existe
echo "Paso 1: Verificando si la imagen '${NOMBRE_IMAGEN_NUEVA}' ya existe..."
if podman images | grep -q "localhost/${USUARIO_SSH}_${NOMBRE_IMAGEN_BASE} *${VERSION_NUEVA}"; then
    echo "La imagen '${NOMBRE_IMAGEN_NUEVA}' ya existe. Omitiendo el paso de construcción."
else
    echo "La imagen no existe. Construyendo la imagen..."
    podman build -t "${NOMBRE_IMAGEN_NUEVA}" -f Dockerfile.backend . || handle_error $LINENO
    echo "Construcción de la imagen '${NOMBRE_IMAGEN_NUEVA}' completada."
fi
echo "----------------------------------------------------"

# 2. Verificar si el archivo .tar existe en local y guardarlo si no existe
echo "Paso 2: Verificando si el archivo '${DIRECTORIO_LOCAL}/${NOMBRE_TAR_NUEVA}.tar' existe..."
if [ -f "${DIRECTORIO_LOCAL}/${NOMBRE_TAR_NUEVA}.tar" ]; then
    echo "El archivo tar ya existe. Omitiendo el paso de guardar la imagen."
else
    echo "El archivo tar no existe. Guardando la imagen en archivo tar..."
    podman save -o "${DIRECTORIO_LOCAL}/${NOMBRE_TAR_NUEVA}.tar" "${NOMBRE_IMAGEN_NUEVA}" || handle_error $LINENO
    echo "Archivo tar guardado con éxito."
fi
echo "----------------------------------------------------"

# 3. Verificar si el archivo .tar existe en el servidor y enviar si no existe
echo "Paso 3: Verificando si el archivo tar existe en el servidor..."
RUTA_SERVIDOR_ARCHIVO_TAR="${RUTA_DESTINO}/${NOMBRE_TAR_NUEVA}.tar"
if ssh "$USUARIO_SSH@$IP_SERVIDOR" "test -f '$RUTA_SERVIDOR_ARCHIVO_TAR'"; then
    echo "El archivo tar ya existe en el servidor. Omitiendo el envío."
else
    echo "El archivo tar no existe en el servidor. Enviando el archivo tar al servidor..."
    scp "${DIRECTORIO_LOCAL}/${NOMBRE_TAR_NUEVA}.tar" "$USUARIO_SSH@$IP_SERVIDOR:$RUTA_SERVIDOR_ARCHIVO_TAR" || handle_error $LINENO
    echo "Archivo tar enviado al servidor con éxito."
fi
echo "----------------------------------------------------"

# 4. Verificar si la imagen ya está cargada en el servidor y cargarla si no está
echo "Paso 4: Comprobando si la imagen '${NOMBRE_IMAGEN_NUEVA}' ya está cargada en el servidor..."
if ssh "$USUARIO_SSH@$IP_SERVIDOR" "podman images | grep -q 'localhost/${USUARIO_SSH}_${NOMBRE_IMAGEN_BASE} *${VERSION_NUEVA}'"; then
    echo "La imagen ya está cargada en el servidor. Procediendo a los demás pasos..."
else
    echo "La imagen no está cargada en el servidor. Cargando la imagen desde el archivo tar..."
    ssh "$USUARIO_SSH@$IP_SERVIDOR" "podman load -i $RUTA_SERVIDOR_ARCHIVO_TAR" || handle_error $LINENO
    echo "Imagen cargada desde el archivo tar."
fi

# Obtener el ID del contenedor de la nueva imagen
echo "Obtener el ID del contenedor de la nueva imagen"
ID_IMAGEN_NUEVA=$(ssh "$USUARIO_SSH@$IP_SERVIDOR" "podman images --filter 'reference=localhost/${USUARIO_SSH}_${NOMBRE_IMAGEN_BASE}:${VERSION_NUEVA}' --format '{{.ID}}' | head -n 1 2>/dev/null")
echo "ID del contenedor de la nueva imagen: $ID_IMAGEN_NUEVA"
echo "----------------------------------------------------"

# 5. Detener contenedor que use el mismo puerto
echo "Paso 5: Verificando si hay contenedores usando el puerto 8097..."
ID_CONTENEDOR_PUERTO=$(ssh "$USUARIO_SSH@$IP_SERVIDOR" "podman ps --format '{{.ID}} {{.Ports}}' | grep '8097' | awk '{print \$1}' 2>/dev/null")

if [ -z "$ID_CONTENEDOR_PUERTO" ]; then
    echo "No hay contenedores usando el puerto 8097."
else
    echo "Contenedor usando puerto 8097: $ID_CONTENEDOR_PUERTO"
    echo "Deteniendo contenedor que usa el puerto..."
    ssh "$USUARIO_SSH@$IP_SERVIDOR" "podman stop $ID_CONTENEDOR_PUERTO" || handle_error $LINENO
    echo "Contenedor detenido con éxito."
fi
echo "----------------------------------------------------"

# 6. Ejecutando el nuevo contenedor
echo "Paso 6: Ejecutando el nuevo contenedor..."
echo "Copiando el archivo .env.production al servidor..."
scp "$DIRECTORIO_LOCAL/.env.production" "$USUARIO_SSH@$IP_SERVIDOR:$RUTA_DESTINO/" || handle_error $LINENO
echo "Archivo .env.production copiado con éxito."

ssh "$USUARIO_SSH@$IP_SERVIDOR" "
    cd Desarrollos/images/ && \
    podman run -d --name ${NOMBRE_TAR_NUEVA} -p $IP_SERVIDOR:8097:8000 -v ll8202_tournament_gaming_media:/code/media --env-file .env.production ${ID_IMAGEN_NUEVA}
" || handle_error $LINENO
echo "Nuevo contenedor '${NOMBRE_TAR_NUEVA}' ejecutado con éxito."
echo "----------------------------------------------------"

# 7. Esperar a que el contenedor se inicie
echo "Paso 7: Esperando 15 segundos para que el contenedor se inicie correctamente..."
sleep 15

# 8. Verificar logs finales
echo "Paso 8: Verificando logs del contenedor..."
ssh "$USUARIO_SSH@$IP_SERVIDOR" "podman logs --tail 10 ${NOMBRE_TAR_NUEVA}" || handle_error $LINENO

echo "===================================================="
echo "           DEPLOY COMPLETADO EXITOSAMENTE           "
echo "Backend: http://10.150.153.31:8097/api/"
echo "===================================================="
