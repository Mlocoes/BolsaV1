#!/bin/bash
# Script para hacer push de FASE 3 a GitHub

echo "🚀 Push de FASE 3 - Sistema de Autenticación Multi-Usuario"
echo "============================================================"
echo ""

# Verificar estado del repositorio
echo "📊 Estado del repositorio:"
git log --oneline -3
echo ""

# Verificar que estamos en la rama correcta
echo "🔍 Rama actual:"
git branch --show-current
echo ""

# Verificar cambios pendientes
echo "📋 Estado de Git:"
git status --porcelain
echo ""

# Mostrar información del commit de FASE 3
echo "📦 Commit de FASE 3:"
git show --stat HEAD
echo ""

echo "⚡ Para hacer push manualmente, ejecuta:"
echo "   git push origin main"
echo ""

echo "🔑 Si tienes problemas de autenticación:"
echo "   1. Configura un token de acceso personal en GitHub"
echo "   2. Usa: git push https://TOKEN@github.com/Mlocoes/BolsaV1.git main"
echo "   3. O configura SSH keys"
echo ""

echo "✅ Commit local completado exitosamente!"
echo "   Hash: $(git rev-parse HEAD)"
echo "   Archivos modificados: $(git diff --name-only HEAD^ HEAD | wc -l)"
echo "   Líneas agregadas: $(git diff --stat HEAD^ HEAD | tail -1)"