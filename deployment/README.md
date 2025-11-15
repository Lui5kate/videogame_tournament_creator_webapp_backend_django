# 🚀 Deployment Guide - Tournament Gaming v2.5

## 📋 **Scripts Disponibles**

### **Deploy Individual**
```bash
# Solo Backend
./deployment/cicd-deploy.sh

# Solo Frontend  
./deployment/cicd-deploy-frontend.sh
```

### **Deploy Completo**
```bash
# Backend + Frontend
./deployment/cicd-deploy-full.sh
```

## 🔧 **Configuración Previa**

1. **Editar .env.production** con credenciales reales
2. **Verificar acceso SSH** al servidor
3. **Confirmar MySQL** en `10.150.153.31:8090`

## 📊 **Puertos Configurados**

- **Frontend:** `10.150.153.31:8096`
- **Backend:** `10.150.153.31:8097`
- **MySQL:** `10.150.153.31:8090` (externo)

## 🐳 **Volúmenes Podman**

- **Media:** `ll8202_tournament_gaming_media:/code/media`

## ⚡ **Deploy Rápido**

```bash
# 1. Configurar variables
cp .env.production .env
# Editar .env con credenciales reales

# 2. Deploy completo
./deployment/cicd-deploy-full.sh
```
