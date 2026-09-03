#!/usr/bin/env bash
set -e

# Directorio base del proyecto
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Colores para la terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}   📊 Sistema de Camino Crítico (CPM / PERT)          ${NC}"
echo -e "${BLUE}======================================================${NC}"

# Verificar y preparar entorno virtual si no existe
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Entorno virtual no detectado. Inicializando con uv sync...${NC}"
    uv sync
fi

# Activar entorno virtual
source .venv/bin/activate

# Modo de ejecución según argumentos
case "$1" in
    test)
        echo -e "${GREEN}Ejecutando suite de pruebas con pytest...${NC}"
        uv run pytest tests/ -v
        ;;
    check)
        echo -e "${GREEN}Ejecutando matriz de verificación completa de calidad...${NC}"
        echo -e "1/4: Ruff linter & format..."
        uv run ruff check .
        uv run ruff format --check .
        echo -e "2/4: Pyright análisis estático de tipos..."
        uv run pyright src/
        echo -e "3/4: Guantelete de restricciones AST..."
        uv run python3 tests/test_architecture.py
        echo -e "4/4: Pytest suite..."
        uv run pytest tests/ -v
        echo -e "${GREEN}✓ Todas las verificaciones superadas con éxito.${NC}"
        ;;
    *)
        HOST="${HOST:-127.0.0.1}"
        PORT="${PORT:-8000}"
        echo -e "${GREEN}Iniciando servidor FastAPI en http://${HOST}:${PORT}${NC}"
        echo -e "${BLUE}Documentación OpenAPI disponible en http://${HOST}:${PORT}/docs${NC}"
        echo -e "${YELLOW}Presione Ctrl+C para detener el servidor.${NC}\n"
        exec uv run uvicorn src.main:app --reload --host "$HOST" --port "$PORT"
        ;;
esac
