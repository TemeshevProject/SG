#!/usr/bin/env python3
"""Build consolidated CAPEX/OPEX artifact catalog from all historical FEM workbooks."""

from __future__ import annotations

import json
import re
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

BASE = Path(__file__).resolve().parent
HIST_DIR = BASE / "historical"
OUTPUT = BASE / "fem_all_artifacts_prices.xlsx"
META = BASE / "price_catalog_meta.json"

SKIP_SHEETS = re.compile(
    r"(титул|titul|wacc|enpv|ддс|опиу|opiu|структур|index|пок\s*пр|пок\s*чп|"
    r"оценка\s+выгод|оценка\s+эфф|баланс\s+риск|чувствитель|график\s+выплат|"
    r"^займ$|макр|бюдж|база|^итог$|summ|inputs|composition|maintenance|"
    r"depreciation|financing|сэф|сээ|бип|сравнен|расчет\s+тариф|расчет\s+займа|"
    r"расчет\s+поступлен|площ$|ст\s+об|экон\s+пок|оц\s+выг|л ist4|list4|"
    r"действующ|расчет\s+ву|capEx\s+модерн|займ\s+модерн)",
    re.I,
)

CAPEX_SHEETS = re.compile(
    r"(инвест|capex|3\.capex|4\.capex|для\s*capex|2\.1\.1\.|rcou|"
    r"3\.\s*инвест|4\.\s*capex|capEx|с\.m\b|сm\b|расшифров)",
    re.I,
)

OPEX_SHEETS = re.compile(
    r"(экспл|opex|обсл|фот|для\s*opex|для\s*ил|зп\b|4\.\s*opex|7\.\s*opex|"
    r"8\.\s*opex|5\.\s*экспл|6\.\s*обсл|расчет\s+фот|расчет\s+экспл|"
    r"стоимости\s+услуг|4\.1\.фот|cost\b|2\.2\.maintenance|штраф)",
    re.I,
)

NAME_HEADERS = (
    "наименование",
    "должность",
    "наименование ",
    "наименование работ",
    "наименование раздела",
)

PRICE_HEADERS = (
    ("итоговая стоимость", 110),
    ("себестоимость за ед.с ндс", 100),
    ("себестоимость за ед", 100),
    ("цена за ед", 100),
    ('зп "к начислению"', 90),
    ("зп к начислению", 90),
    ("оклад с учетом налогов", 90),
    ("зп на руки", 85),
    ("цена в мес", 80),
    ("цена в мес, тыс", 75),
    ("затраты в год", 70),
    ("стоимость работ", 68),
    ("стоимость оборудования", 67),
    ("итого себестоимость", 65),
)


def is_qty_header(h: str) -> bool:
    return ("кол" in h or "кол-во" in h) and "себест" not in h and "затрат" not in h


def pick_price_columns(headers: dict[int, str]) -> list[tuple[int, int]]:
    scored = []
    for c, h in headers.items():
        if is_qty_header(h):
            continue
        for needle, score in PRICE_HEADERS:
            if needle in h:
                scored.append((score, c))
                break
    scored.sort(reverse=True)
    return scored

EXCLUDE_NAME = re.compile(
    r"(^итого|^всего|^амортизац|^остаточн|^№\s*п/п$|"
    r"^наименование$|^наименование\s+(показател|работ|товара|оборудования|раздела)|"
    r"^описание$|^товар$|^должность$|^фот,?\s*тенге$|"
    r"инвестиционные\s+затрат|операционные\s+затрат|"
    r"^техническая\s+спецификация|^расчет\s+общих|"
    r"^площадь\s+для\s+размещ|^расходы\s+по\s+фот\s+в\s+разрезе|"
    r"на\s+начало\s+года|на\s+конец\s+года|^кол-?во\s+узлов|"
    r"^расходы\s+по\s+объекту\s+предназначенному|"
    r"^\d\.\s*(административно|производственный)\s+персонал|"
    r"^\d+[\.\)]?\s*$|^none$|^\d{4}[\.\-]\d+$)",
    re.I,
)

# Rows from the "потребность в площадях" blocks: square metres, not money.
AREA_ROW = re.compile(
    r"^(зал\s+совещан|гардероб|комната\s+(приема|приёма|отдыха|ожидан)|"
    r"помещение\s+ожидан|туалет|кладовая)",
    re.I,
)

UNIT_TENGE = "тенге"
UNIT_TENGE_MONTH = "тенге/мес"
UNIT_THOUSAND_MONTH = "тыс. тенге/мес"
UNIT_TENGE_YEAR = "тенге/год"
UNIT_THOUSAND_YEAR = "тыс. тенге/год"
UNIT_SALARY_MONTH = "тенге/мес (на 1 сотрудника)"


def detect_unit(headers: dict[int, str], price_col: int, kind: str) -> str:
    h = headers.get(price_col, "")
    thousands = "тыс" in h
    if "оклад" in h or "зп" in h:
        return UNIT_SALARY_MONTH
    if "в год" in h or "год" in h:
        return UNIT_THOUSAND_YEAR if thousands else UNIT_TENGE_YEAR
    if "в мес" in h or "мес" in h:
        return UNIT_THOUSAND_MONTH if thousands else UNIT_TENGE_MONTH
    if kind == "OPEX":
        return UNIT_TENGE_MONTH if "цена" in h else UNIT_TENGE
    return UNIT_TENGE


def norm(text) -> str:
    if text is None:
        return ""
    s = str(text).strip().lower().replace("ё", "е")
    s = re.sub(r"\s+", " ", s)
    return s


def to_float(val):
    if val is None:
        return None
    if isinstance(val, (int, float)):
        if isinstance(val, float) and (val != val):  # NaN
            return None
        return float(val)
    s = str(val).strip().replace(" ", "").replace(",", ".")
    if not s or s in {"-", "#REF!", "#N/A"}:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def classify_from_headers(headers: dict[int, str]) -> str | None:
    joined = " ".join(headers.values())
    if "себестоимость за ед" in joined or "итого себестоимость" in joined:
        return "CAPEX"
    if any(x in joined for x in ("цена в мес", "затраты в год", "зп на руки", "зп к начислению", "оклад с учетом")):
        return "OPEX"
    return None


def classify_sheet(sheet_name: str, ws, headers: dict[int, str] | None = None) -> str | None:
    sn = norm(sheet_name)
    if SKIP_SHEETS.search(sheet_name):
        return None
    if CAPEX_SHEETS.search(sheet_name):
        return "CAPEX"
    if OPEX_SHEETS.search(sheet_name):
        return "OPEX"
    if headers:
        h_kind = classify_from_headers(headers)
        if h_kind:
            return h_kind
    blob = ""
    for r in range(1, 8):
        for c in range(1, 6):
            v = ws.cell(r, c).value
            if v:
                blob += " " + str(v).lower()
    if "инвестицион" in blob and "затрат" in blob:
        return "CAPEX"
    if "операцион" in blob or "эксплуатац" in blob:
        return "OPEX"
    if "наименование" in blob and ("себестоимость" in blob or "инвест" in blob):
        return "CAPEX"
    if "наименование" in blob and ("цена в мес" in blob or "затраты в год" in blob):
        return "OPEX"
    return None


def read_header_row(ws, r: int) -> dict[int, str]:
    headers = {}
    for c in range(1, min(ws.max_column, 25) + 1):
        h = norm(ws.cell(r, c).value)
        if h:
            headers[c] = h
    return headers


def parse_header_row(headers: dict[int, str]):
    name_col = None
    for c, h in headers.items():
        if any(h.startswith(n.strip()) or n.strip() in h for n in NAME_HEADERS):
            name_col = c
            break
    if not name_col:
        return None
    price_col = None
    price_score = -1
    for c, h in headers.items():
        if is_qty_header(h):
            continue
        for needle, score in PRICE_HEADERS:
            if needle in h and score > price_score:
                price_col = c
                price_score = score
    if not price_col:
        return None
    return name_col, price_col


def find_table_blocks(ws, max_scan_rows: int = 400) -> list[dict]:
    """FEM sheets stack several independent tables, each with its own header row."""
    blocks = []
    limit = min(ws.max_row, max_scan_rows)
    for r in range(1, limit + 1):
        headers = read_header_row(ws, r)
        if not headers:
            continue
        parsed = parse_header_row(headers)
        if not parsed:
            continue
        name_col, price_col = parsed
        blocks.append(
            {
                "header_row": r,
                "name_col": name_col,
                "price_col": price_col,
                "headers": headers,
            }
        )
    for i, blk in enumerate(blocks):
        blk["end_row"] = blocks[i + 1]["header_row"] - 1 if i + 1 < len(blocks) else ws.max_row
    return blocks


def is_valid_name(name: str) -> bool:
    if not name or len(name.strip()) < 3:
        return False
    n = norm(name)
    if EXCLUDE_NAME.search(n):
        return False
    if AREA_ROW.match(n):
        return False
    if re.fullmatch(r"[\d\.,\s]+", n):
        return False
    return True


def row_price(
    ws,
    r: int,
    name_col: int,
    headers: dict[int, str],
    header_row: int,
    capex_opex: str,
    primary_col: int,
):
    candidates: list[float] = []
    for _, c in pick_price_columns(headers):
        v = to_float(ws.cell(r, c).value)
        if v is not None and v > 0:
            candidates.append(v)
    if not candidates:
        for c in range(name_col + 1, min(name_col + 12, ws.max_column + 1)):
            h = headers.get(c)
            if h is None:
                h = norm(ws.cell(header_row, c).value)
            if is_qty_header(h):
                continue
            v = to_float(ws.cell(r, c).value)
            if v is not None and v > 0:
                candidates.append(v)
    if not candidates:
        return None

    for c, h in headers.items():
        if "итогов" in h and "стоим" in h:
            total = to_float(ws.cell(r, c).value)
            if total is not None and total > 0:
                return total

    primary = to_float(ws.cell(r, primary_col).value)
    if primary is not None and primary > 0 and not is_qty_header(headers.get(primary_col, "")):
        if capex_opex == "OPEX" or primary >= 1000:
            return primary

    big = [v for v in candidates if v >= 1000]
    if big:
        return max(big)
    return max(candidates)


def extract_sheet(ws, sheet_name: str, fem_name: str, capex_opex: str | None) -> list[dict]:
    out = []
    for block in find_table_blocks(ws):
        out.extend(extract_block(ws, block, sheet_name, fem_name, capex_opex))
    return out


def extract_block(ws, block: dict, sheet_name: str, fem_name: str, capex_opex: str | None) -> list[dict]:
    header_row = block["header_row"]
    name_col = block["name_col"]
    price_col = block["price_col"]
    headers = block["headers"]

    kind = capex_opex or classify_from_headers(headers) or classify_sheet(sheet_name, ws, headers)
    if not kind:
        return []

    unit = detect_unit(headers, price_col, kind)
    out = []
    for r in range(header_row + 1, block["end_row"] + 1):
        name = ws.cell(r, name_col).value
        if not name:
            continue
        name_s = str(name).strip()
        if not is_valid_name(name_s):
            continue
        price = row_price(ws, r, name_col, headers, header_row, kind, price_col)
        out.append(
            {
                "type": kind,
                "name": name_s,
                "price": price,
                "unit": unit,
                "source": f"{fem_name} :: {sheet_name}",
            }
        )
    return out


def extract_workbook(path: Path) -> list[dict]:
    items = []
    try:
        wb = openpyxl.load_workbook(path, data_only=True, read_only=False)
    except Exception as exc:
        print(f"Skip {path.name}: {exc}")
        return items

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        if SKIP_SHEETS.search(sheet_name):
            continue
        kind = classify_sheet(sheet_name, ws)
        items.extend(extract_sheet(ws, sheet_name, path.name, kind))
    wb.close()
    return items


# Порядок важен: правила проверяются сверху вниз, первое совпадение выигрывает.
GROUP_RULES: tuple[tuple[re.Pattern, str, int, str], ...] = (
    (
        re.compile(r"директор|менеджер|инжен[ес]р|инденер|бухгалтер|юрист|экономист|специалист|"
                   r"оператор\b|операторы|аналитик|логист|водитель|секретар|ассистент|техник-|"
                   r"начальник|заместитель|советник|калибровщик|монтажник|бригадир|"
                   r"программист|разработчик|администратор|инспектор|грузчик|заведующ|"
                   r"персонал|\bзп\b|фот\b", re.I),
        "ФОТ (персонал)",
        4,
        "Пересмотр штатного расписания, совмещение ролей, автоматизация рутины, аутсорс непрофильных функций",
    ),
    (
        re.compile(r"билет|проживан|суточн|командиров", re.I),
        "Командировки",
        1,
        "Тревел-политика, корпоративные тарифы, замена части выездов на удалённую работу",
    ),
    (
        re.compile(r"канал\s+(передачи|связи)|каналы\s+связи|интернет|трафик|мбит|провайдер|"
                   r"точк.\s+подключен|подключен.*канал", re.I),
        "Каналы связи и интернет",
        2,
        "Переторжка с операторами, консолидация трафика, пересмотр скорости канала под фактическую нагрузку",
    ),
    (
        re.compile(r"обслуживан|техническое\s+обслуж|юстировк|чистк|замена\s+модул|"
                   r"поверк|непредвиденн|ремонт\b", re.I),
        "Эксплуатация и ТО",
        3,
        "Перевод на собственную службу вместо подряда, пересмотр SLA и регламентной периодичности",
    ),
    (
        re.compile(r"ибезопасн|информационн.*безопасн|\bips\b|\bdlp\b|\bsiem\b|фаервол|firewall|"
                   r"fortigate|ngfw|гтс|испытан.*иб|аттестац", re.I),
        "Информационная безопасность",
        5,
        "Требования регулятора: снижение возможно только через изменение архитектуры и объёма аттестации",
    ),
    (
        re.compile(r"лиценз|vmware|vsphere|veeam|kaspersky|microsoft|windows|подписк|"
                   r"программное\s+обеспечен|\bvms\b|subscription|license|"
                   r"поддержка\s+и\s+обновление\s+п", re.I),
        "Лицензии и ПО",
        4,
        "Переход на open-source/отечественные аналоги, пересмотр числа лицензий, перевод perpetual→подписка",
    ),
    (
        # Только работы: названия оборудования часто содержат "...для монтажа".
        re.compile(r"^(монтаж|настройка|пусконаладк|пуско-наладк|инсталя|строительн|"
                   r"ремонтно|креплен|навеск|прокладк|логистик|сети\s+электропитан)|"
                   r"монтажные\s+и\s+инсталя|работы\s+по\s+машзал", re.I),
        "Монтаж и СМР",
        3,
        "Конкурс среди подрядчиков, типовые решения монтажа, укрупнение лотов по географии",
    ),
    (
        re.compile(r"апк|сергек|линейн(ый|ые)\s+участ|перекрест|патруль|трасс", re.I),
        "АПК «Сергек»",
        4,
        "Собственный продукт: удешевление через ревизию спецификации, локализацию сборки и переход на альтернативные комплектующие",
    ),
    (
        re.compile(r"камер|овн\b|варифакальн|фиксированн|поворотн|интеграц|объект\s+размещ|"
                   r"видеорегистратор|видеонаблюден", re.I),
        "Камеры ОВН и интеграция",
        2,
        "Массовая закупка: тендер, прямой контракт с вендором, отказ от избыточных характеристик",
    ),
    (
        re.compile(r"сервер|схд|система\s+хранения|цод|цоу|рцоу|дата-?центр|серверн|коммутацион|"
                   r"стойк|шкаф\s+серверн|ибп\b|бесперебойн|дизель|охлажден|фальш|"
                   r"центр\s+обработки", re.I),
        "ЦОД и серверное оборудование",
        3,
        "Пересмотр запаса мощности, аренда мощностей вместо покупки, вторичный рынок и продление гарантии",
    ),
    (
        re.compile(r"метеостанц|метеодатчик|датчик\s+(pm|качества)", re.I),
        "Метеостанции и датчики",
        3,
        "Выбор менее дорогих моделей датчиков, пересмотр плотности размещения по городу",
    ),
    (
        re.compile(r"аренда\s+помещ|аренда\s+цод|аренда\s+точ|аренда", re.I),
        "Аренда помещений",
        2,
        "Переговоры по ставке, сокращение площадей, релокация в менее дорогую локацию",
    ),
    (
        re.compile(r"электроэнерг|коммунальн|дт\s+для|гсм|топлив", re.I),
        "Энергия и ГСМ",
        4,
        "Тариф регулируется рынком: экономия через энергоэффективность и снижение потребления",
    ),
    (
        re.compile(r"охран|клининг|канц|хоз\.?\s*товар|питьев|диспенсер|"
                   r"микроволнов|холодильник|уборк", re.I),
        "Хозяйственные расходы",
        1,
        "Тендер среди поставщиков услуг, пересмотр нормативов расхода",
    ),
    (
        re.compile(r"мебель|стол|стул|кресло|тумба|шкаф|сейф|доска\s+магнит", re.I),
        "Мебель и обстановка",
        1,
        "Прямые закупки у производителя, типовая комплектация, отказ от премиального сегмента",
    ),
    (
        re.compile(r"спецовк|перчатк|каска|обувь|дождевик|жилет|желет|очки\s+защ|"
                   r"страховочн|диэлектрическ|стропы|боты|фонарик|сиз", re.I),
        "СИЗ и спецодежда",
        1,
        "Консолидированная закупка, переход на отечественных производителей",
    ),
    (
        re.compile(r"перфоратор|шуруповерт|дрель|мультиметр|тестер|инструмент|"
                   r"стремянк|сумка|рюкзак|молоток|нож\s|ключей|пробник|батарея\s+в\s|"
                   r"зарядное\s+устройств", re.I),
        "Инструмент и оснастка",
        2,
        "Единый поставщик, переход с премиальных брендов на средний сегмент",
    ),
    (
        re.compile(r"ноутбук|компьютер|монитор|мфу|принтер|клавиатур|процессор|"
                   r"видеокарт|материнск|ssd|dimm|блок\s+питания|корпус|кулер|"
                   r"jabra|nuc|планшет|рации|рация|радиостанц|ip-?телефон|"
                   r"wifi|роутер|маршрутизатор|коммутатор|патч|patch|кабел|кабель|sfp|"
                   r"power\s+cord|transceiver|disk|enclosure|мобильное\s+рабочее|"
                   r"удлинитель|картридж", re.I),
        "Рабочие места и ИТ-периферия",
        2,
        "Стандартизация конфигураций, корпоративные цены вендоров, увеличение срока службы",
    ),
    (
        re.compile(r"ситуацион|видеостен|панел|арм\b|рабочее\s+место\s+оператор|"
                   r"видеоконференц|интерактивн", re.I),
        "Ситуационный центр",
        3,
        "Пересмотр состава видеостены и числа АРМ под фактическую нагрузку операторов",
    ),
    (
        re.compile(r"скуд|домофон|замок|турникет|карта\s+доступ|распознаван|"
                   r"контрол.*доступ|кнопка\s+выхода|доводчик|сигнализац|пожаротуш|"
                   r"кондиционер|счетчик|аскуэ", re.I),
        "Инженерные системы объекта",
        2,
        "Типовые проектные решения, конкурс подрядчиков, унификация оборудования",
    ),
    (
        re.compile(r"независимая\s+оценка|экспертиз|проектно-изыскат|надзор|"
                   r"сопровожден|консультац", re.I),
        "Проектирование и экспертиза",
        3,
        "Конкурс среди проектных организаций, повторное использование типовых проектов",
    ),
)

DEFAULT_GROUP = ("Прочее", 3, "Требуется ручная классификация и определение рычага снижения")


def classify_group(name: str, kind: str) -> tuple[str, int, str]:
    for pattern, group, score, lever in GROUP_RULES:
        if pattern.search(name):
            return group, score, lever
    return DEFAULT_GROUP


COMPLEXITY_LABELS = {
    1: "1 — низкая",
    2: "2 — ниже средней",
    3: "3 — средняя",
    4: "4 — высокая",
    5: "5 — очень высокая",
}


def enrich(rows: list[dict]) -> list[dict]:
    for row in rows:
        group, score, lever = classify_group(row["name"], row["type"])
        row["group"] = group
        row["complexity"] = score
        row["complexity_label"] = COMPLEXITY_LABELS[score]
        row["lever"] = lever

        # В части исходных ФЭМ колонки съезжают и вместо цены стоит количество.
        price = row.get("price")
        if price is None or price <= 0:
            row["unit"] = "цена не указана"
        elif row["type"] == "CAPEX" and price < 1000:
            row["unit"] = f"{row.get('unit', UNIT_TENGE)} (проверить: похоже на количество)"
    return rows


def dedupe_max_price(items: list[dict]) -> list[dict]:
    buckets: dict[str, list[dict]] = {}
    for it in items:
        key = (it["type"], norm(it["name"]))
        buckets.setdefault(key, []).append(it)

    result = []
    for key, group in buckets.items():
        with_price = [g for g in group if g["price"] is not None and g["price"] > 0]
        if with_price:
            best = max(with_price, key=lambda x: x["price"])
        else:
            best = group[0]
        result.append(best)
    result.sort(key=lambda x: (x["type"], norm(x["name"])))
    return result


HEADERS = [
    "CAPEX/OPEX",
    "Группа",
    "Наименование артефакта",
    "Цена",
    "Ед. изм.",
    "Сложность снижения",
    "Рычаг снижения цены",
    "Источник",
]

COLUMN_WIDTHS = {
    "A": 12,
    "B": 30,
    "C": 62,
    "D": 16,
    "E": 22,
    "F": 20,
    "G": 62,
    "H": 52,
}

COMPLEXITY_FILL = {
    1: "C6EFCE",
    2: "DDEBCD",
    3: "FFEB9C",
    4: "FCD5B4",
    5: "FFC7CE",
}


def fill_sheet(ws, data: list[dict]):
    ws.append(HEADERS)
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="D9E1F2")
        cell.alignment = Alignment(vertical="center", wrap_text=True)

    for row in data:
        ws.append(
            [
                row["type"],
                row["group"],
                row["name"],
                row["price"],
                row.get("unit"),
                row["complexity_label"],
                row["lever"],
                row["source"],
            ]
        )
        complexity_cell = ws.cell(ws.max_row, 6)
        complexity_cell.fill = PatternFill("solid", fgColor=COMPLEXITY_FILL[row["complexity"]])
        price_cell = ws.cell(ws.max_row, 4)
        price_cell.number_format = "#,##0.00"

    for col, width in COLUMN_WIDTHS.items():
        ws.column_dimensions[col].width = width
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:H{ws.max_row}"


def write_summary(ws, rows: list[dict]):
    ws.append(["Группа", "CAPEX/OPEX", "Позиций", "Сложность снижения"])
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="D9E1F2")

    stats: dict[tuple[str, str], dict] = {}
    for row in rows:
        key = (row["group"], row["type"])
        entry = stats.setdefault(key, {"count": 0, "complexity": row["complexity_label"]})
        entry["count"] += 1

    for (group, kind), entry in sorted(stats.items(), key=lambda x: -x[1]["count"]):
        ws.append([group, kind, entry["count"], entry["complexity"]])

    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 22
    ws.freeze_panes = "A2"


def write_output(rows: list[dict]):
    wb = openpyxl.Workbook()

    ws_all = wb.active
    ws_all.title = "Все артефакты"
    fill_sheet(ws_all, rows)

    for title in ("CAPEX", "OPEX"):
        fill_sheet(wb.create_sheet(title), [r for r in rows if r["type"] == title])

    write_summary(wb.create_sheet("Сводка по группам"), rows)
    wb.save(OUTPUT)


def main():
    if not HIST_DIR.exists():
        raise SystemExit(f"Missing {HIST_DIR}")

    raw = []
    for path in sorted(HIST_DIR.glob("*.xlsx")):
        extracted = extract_workbook(path)
        print(f"{path.name}: {len(extracted)} rows")
        raw.extend(extracted)

    deduped = enrich(dedupe_max_price(raw))
    write_output(deduped)

    by_group: dict[str, int] = {}
    by_complexity: dict[str, int] = {}
    for row in deduped:
        by_group[row["group"]] = by_group.get(row["group"], 0) + 1
        by_complexity[row["complexity_label"]] = by_complexity.get(row["complexity_label"], 0) + 1

    meta = {
        "historical_files": len(list(HIST_DIR.glob("*.xlsx"))),
        "raw_rows": len(raw),
        "unique_artifacts": len(deduped),
        "capex": sum(1 for r in deduped if r["type"] == "CAPEX"),
        "opex": sum(1 for r in deduped if r["type"] == "OPEX"),
        "with_price": sum(1 for r in deduped if r["price"] is not None and r["price"] > 0),
        "by_group": dict(sorted(by_group.items(), key=lambda x: -x[1])),
        "by_complexity": dict(sorted(by_complexity.items())),
        "output": str(OUTPUT.name),
    }
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
