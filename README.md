# SG — Калькулятор себестоимости АПК Сергек

Платформа-конструктор для расчёта спецификации и себестоимости аппаратно-программного комплекса.

## Запуск на вашем компьютере

**Агент не может запускать программы на вашем ПК** — только в облаке. Чтобы открыть `localhost`, запустите проект локально:

### Windows — двойной клик
`scripts\start-windows.bat`

### Mac / Linux
```bash
./scripts/start-mac.sh
# или
./scripts/dev.sh
```

### Вручную (два терминала)
```bash
# Терминал 1
cd backend && pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Терминал 2
cd frontend && npm install && npm run dev
```

Откройте: **http://localhost:5173**

Нужны: [Python 3](https://python.org) и [Node.js](https://nodejs.org).

## Структура

- `data/bom-templates/` — шаблоны BOM с формулами (ЛУ/П × Dahua/Hikvision)
- `data/price-catalog/` — справочники закупочных цен
- `backend/` — API расчёта и экспорт Excel
- `frontend/` — веб-конструктор проекта
