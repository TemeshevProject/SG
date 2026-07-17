# SG — Калькулятор себестоимости АПК Сергек

Платформа-конструктор для расчёта спецификации и себестоимости аппаратно-программного комплекса.

## Запуск на вашем компьютере

Серверы в облаке агента **не доступны** по `localhost` на вашей машине — нужно запустить проект локально:

```bash
git clone https://github.com/TemeshevProject/SG.git
cd SG
git checkout cursor/apk-cost-calculator-4559

# Один скрипт (backend + frontend)
./scripts/dev.sh
```

Или в двух терминалах:

```bash
# Терминал 1 — API
cd backend && pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Терминал 2 — UI
cd frontend && npm install && npm run dev
```

Откройте: **http://localhost:5173**

> Excel-файлы спецификаций должны лежать в `drive-input/` для импорта BOM (`python3 scripts/import_bom.py`). Справочники цен и шаблоны BOM уже в репозитории.

## Структура

- `data/bom-templates/` — шаблоны BOM с формулами (ЛУ/П × Dahua/Hikvision)
- `data/price-catalog/` — справочники закупочных цен
- `backend/` — API расчёта и экспорт Excel
- `frontend/` — веб-конструктор проекта
