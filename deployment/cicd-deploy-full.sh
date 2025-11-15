#!/bin/bash

echo "===================================================="
echo "      DEPLOY COMPLETO TOURNAMENT GAMING v2.5       "
echo "===================================================="

# 1. Deploy Backend
echo "🔧 INICIANDO DEPLOY BACKEND..."
./deployment/cicd-deploy.sh
if [ $? -ne 0 ]; then
    echo "❌ Error en deploy backend"
    exit 1
fi

echo ""
echo "🎨 INICIANDO DEPLOY FRONTEND..."
# 2. Deploy Frontend
./deployment/cicd-deploy-frontend.sh
if [ $? -ne 0 ]; then
    echo "❌ Error en deploy frontend"
    exit 1
fi

echo ""
echo "===================================================="
echo "         DEPLOY COMPLETO EXITOSO                    "
echo "===================================================="
echo "🌐 Frontend: http://10.150.153.31:8096"
echo "🔧 Backend:  http://10.150.153.31:8097/api/"
echo "===================================================="
