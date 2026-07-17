#!/usr/bin/env bash
# Локальный запуск калькулятора (backend + frontend)
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if ! command -v python3 >/dev/null; then
  echo "Нужен python3"
  exit 1
fi
if ! command -v npm >/dev/null; then
  echo "Нужен npm (Node.js)"
  exit 1
fi

echo "==> Установка зависимостей..."
pip install -q -r "$ROOT/backend/requirements.txt"
if [ ! -d "$ROOT/frontend/node_modules" ]; then
  (cd "$ROOT/frontend" && npm install)
fi

if [ ! -f "$ROOT/data/bom-templates/lu-hikvision.json" ]; then
  echo "==> Импорт BOM из Excel..."
  python3 "$ROOT/scripts/import_bom.py"
fi

cleanup() {
  kill "$BACK_PID" "$FRONT_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo "==> Backend http://127.0.0.1:8000"
(cd "$ROOT/backend" && PYTHONPATH=. python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000) &
BACK_PID=$!

sleep 1

echo "==> Frontend http://127.0.0.1:5173"
(cd "$ROOT/frontend" && npm run dev -- --host 127.0.0.1 --port 5173) &
FRONT_PID=$!

echo ""
echo "Откройте в браузере: http://localhost:5173"
echo "Остановка: Ctrl+C"
wait
