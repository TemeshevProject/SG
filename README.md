# SG — Калькулятор себестоимости АПК Сергек

Платформа-конструктор для расчёта спецификации и себестоимости аппаратно-программного комплекса.

## Запуск

```bash
# Backend (порт 8000)
cd backend && PYTHONPATH=. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (порт 5173)
cd frontend && npm run dev
```

Импорт BOM из Excel (при обновлении спецификаций):

```bash
python3 scripts/import_bom.py
```

## Структура

- `data/bom-templates/` — шаблоны BOM с формулами (ЛУ/П × Dahua/Hikvision)
- `data/price-catalog/` — справочники закупочных цен
- `backend/` — API расчёта и экспорт Excel
- `frontend/` — веб-конструктор проекта
