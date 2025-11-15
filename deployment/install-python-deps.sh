#!/bin/bash
# Instalar dependencias Python desde archivos locales
echo "📦 Instalando dependencias Python desde archivos locales..."
pip install --no-index --find-links deployment/python-deps/ -r requirements.txt
echo "✅ Dependencias Python instaladas"
