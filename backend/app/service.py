from __future__ import annotations

from app.bom.calculator import aggregate_line_items, calculate_apk_bom
from app.models import ProjectRequest, ProjectSummary


def _config_label(cfg) -> str:
    seg = "ЛУ" if cfg.segment == "LU" else "П"
    pwr = "П.П." if cfg.power_type == "constant" else "Освещ."
    return cfg.label or f"{seg} · {pwr} · {cfg.apk_count} шт."


def calculate_project(req: ProjectRequest) -> ProjectSummary:
    all_items: list[dict] = []
    config_summaries = []

    for cfg in req.configurations:
        label = _config_label(cfg)
        items = calculate_apk_bom(cfg, req.manufacturer)
        subtotal = sum(i["total_price_kzt"] or 0 for i in items)
        for item in items:
            item["config_label"] = label
            item["segment"] = cfg.segment
            item["power_type"] = cfg.power_type
        all_items.extend(items)
        config_summaries.append(
            {
                "label": label,
                "segment": cfg.segment,
                "power_type": cfg.power_type,
                "apk_count": cfg.apk_count,
                "line_count": len(items),
                "subtotal_kzt": round(subtotal, 2) if subtotal else None,
            }
        )

    consolidated = aggregate_line_items(all_items)
    total = sum(c["total_price_kzt"] or 0 for c in consolidated)
    missing = sum(1 for c in consolidated if c["unit_price_kzt"] is None)

    return ProjectSummary(
        name=req.name,
        apk_version=req.apk_version,
        manufacturer=req.manufacturer,
        configurations=config_summaries,
        line_items=all_items,
        consolidated=consolidated,
        total_cost_kzt=round(total, 2) if total else None,
        missing_prices=missing,
    )
