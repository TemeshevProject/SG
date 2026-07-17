"""BOM template loading and per-APK quantity calculation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from app.bom.formulas import resolve_quantities
from app.models import ApkConfiguration, PowerType, SegmentType

ROOT = Path(__file__).resolve().parents[3]
TEMPLATES_DIR = ROOT / "data" / "bom-templates"
PRICES_DIR = ROOT / "data" / "price-catalog"

# Per-segment Excel row anchors for driver cells (column G/H row numbers)
SEGMENT_DRIVERS = {
    "LU": {"hr_camera": 7, "strobe": 8, "cabinet": 15, "radar": 51},
    "P": {"hr_camera": 9, "strobe": 10, "cabinet": 17, "radar": 54},
}


def load_template(segment: SegmentType, manufacturer: str) -> dict:
    path = TEMPLATES_DIR / f"{segment.lower()}-{manufacturer.lower()}.json"
    if not path.exists():
        raise FileNotFoundError(f"BOM template not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_price_catalog(segment: SegmentType, manufacturer: str) -> dict[str, float]:
    path = PRICES_DIR / f"{segment.lower()}-{manufacturer.lower()}.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        item["name"]: item["unit_price_kzt"]
        for item in data.get("items", [])
        if item.get("unit_price_kzt") is not None
    }


def _col_prefix(power_type: PowerType) -> str:
    return "G" if power_type == "constant" else "H"


def build_drivers(cfg: ApkConfiguration) -> dict[str, float]:
    anchors = SEGMENT_DRIVERS[cfg.segment]
    col = _col_prefix(cfg.power_type)
    drivers: dict[str, float] = {}

    # Cabinet: 1 per APK
    drivers[f"{col}{anchors['cabinet']}"] = 1.0

    if cfg.hr_camera.enabled and cfg.hr_camera.directions:
        n_dir = len(cfg.hr_camera.directions)
        total_lanes = sum(d.lanes for d in cfg.hr_camera.directions)
        drivers[f"{col}{anchors['hr_camera']}"] = float(n_dir)
        drivers[f"{col}{anchors['strobe']}"] = float(total_lanes)
    else:
        drivers[f"{col}{anchors['hr_camera']}"] = 0.0
        drivers[f"{col}{anchors['strobe']}"] = 0.0

    if cfg.radar.enabled and cfg.radar.directions:
        drivers[f"{col}{anchors['radar']}"] = float(len(cfg.radar.directions))
    else:
        drivers[f"{col}{anchors['radar']}"] = 0.0

    return drivers


def calculate_apk_bom(cfg: ApkConfiguration, manufacturer: str) -> list[dict]:
    template = load_template(cfg.segment, manufacturer)
    rows = template["rows"]
    power_key: Literal["constant", "lighting"] = cfg.power_type
    drivers = build_drivers(cfg)
    quantities = resolve_quantities(rows, power_key, drivers)
    prices = load_price_catalog(cfg.segment, manufacturer)

    line_items = []
    for row in rows:
        r = row["row"]
        qty_per_apk = quantities.get(r, 0.0)
        if qty_per_apk <= 0:
            continue
        total_qty = qty_per_apk * cfg.apk_count
        unit_price = prices.get(row["name"])
        line_items.append(
            {
                "row": r,
                "module": row.get("module"),
                "description": row["description"],
                "name": row["name"],
                "unit": row["unit"],
                "qty_per_apk": round(qty_per_apk, 4),
                "apk_count": cfg.apk_count,
                "total_qty": round(total_qty, 4),
                "unit_price_kzt": unit_price,
                "total_price_kzt": round(total_qty * unit_price, 2)
                if unit_price is not None
                else None,
            }
        )
    return line_items


def aggregate_line_items(all_items: list[dict]) -> list[dict]:
    """Merge identical positions across configurations with breakdown."""
    merged: dict[str, dict] = {}
    for item in all_items:
        key = item["name"]
        if key not in merged:
            merged[key] = {
                **{k: item[k] for k in ("row", "module", "description", "name", "unit", "unit_price_kzt")},
                "total_qty": 0.0,
                "total_price_kzt": 0.0,
                "breakdown": [],
            }
        entry = merged[key]
        entry["total_qty"] += item["total_qty"]
        if item["total_price_kzt"] is not None:
            entry["total_price_kzt"] = (entry["total_price_kzt"] or 0) + item["total_price_kzt"]
        entry["breakdown"].append(
            {
                "config_label": item.get("config_label"),
                "segment": item.get("segment"),
                "power_type": item.get("power_type"),
                "apk_count": item["apk_count"],
                "qty_per_apk": item["qty_per_apk"],
                "total_qty": item["total_qty"],
            }
        )
    for entry in merged.values():
        entry["total_qty"] = round(entry["total_qty"], 4)
        if entry["total_price_kzt"]:
            entry["total_price_kzt"] = round(entry["total_price_kzt"], 2)
    return sorted(merged.values(), key=lambda x: x.get("row") or 0)
