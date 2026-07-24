"""Evaluate Excel-style quantity formulas (columns G/H)."""

from __future__ import annotations

import ast
import math
import operator
import re
from typing import Any

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


class FormulaError(Exception):
    pass


def _normalize(expr: str) -> str:
    expr = expr.strip()
    if expr.startswith("="):
        expr = expr[1:]
    # Excel uses ^ for power; treat as Python **
    expr = expr.replace("^", "**")
    return expr


def _replace_cell_refs(expr: str, cells: dict[str, float]) -> str:
    def repl(match: re.Match[str]) -> str:
        col = match.group(1)
        row = match.group(2)
        key = f"{col}{row}"
        val = cells.get(key, 0.0)
        if val is None or (isinstance(val, str) and val == "-"):
            val = 0.0
        return str(float(val))

    # $G$17 or G17
    return re.sub(r"\$?([GH])\$?(\d+)", repl, expr, flags=re.IGNORECASE)


class _SafeEval(ast.NodeVisitor):
    def visit(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Expression):
            return self.visit(node.body)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return float(node.value)
            raise FormulaError(f"Unsupported constant: {node.value!r}")
        if isinstance(node, ast.BinOp):
            left = self.visit(node.left)
            right = self.visit(node.right)
            op = OPS.get(type(node.op))
            if not op:
                raise FormulaError(f"Unsupported operator: {type(node.op)}")
            return float(op(left, right))
        if isinstance(node, ast.UnaryOp):
            operand = self.visit(node.operand)
            op = OPS.get(type(node.op))
            if not op:
                raise FormulaError(f"Unsupported unary: {type(node.op)}")
            return float(op(operand))
        raise FormulaError(f"Unsupported node: {type(node).__name__}")


def eval_formula(formula: str, cells: dict[str, float]) -> float:
    if formula is None or formula == "" or formula == "-":
        return 0.0
    if not isinstance(formula, str):
        return float(formula)
    if not formula.startswith("="):
        try:
            return float(formula)
        except (TypeError, ValueError):
            return 0.0

    expr = _normalize(formula)
    expr = _replace_cell_refs(expr, cells)
    try:
        tree = ast.parse(expr, mode="eval")
        result = _SafeEval().visit(tree)
        if math.isnan(result) or math.isinf(result):
            return 0.0
        return float(result)
    except Exception as exc:
        raise FormulaError(f"Failed to evaluate {formula!r} -> {expr!r}: {exc}") from exc


def resolve_quantities(
    rows: list[dict],
    power_type: str,
    drivers: dict[str, float],
    max_passes: int = 12,
) -> dict[int, float]:
    """
    power_type: 'constant' -> column G (qty_pp), 'lighting' -> column H (qty_light)
    drivers: initial cell values like {'G7': 2, 'G8': 5}
    Returns row_number -> quantity per single APK.
    """
    col_prefix = "G" if power_type == "constant" else "H"
    qty_key = "qty_pp" if power_type == "constant" else "qty_light"
    formula_key = f"{qty_key}_formula"

    cells: dict[str, float] = {k.upper(): float(v) for k, v in drivers.items()}

    # Seed cells from static numeric values in template
    for row in rows:
        r = row["row"]
        key = f"{col_prefix}{r}"
        raw = row.get(qty_key)
        if isinstance(raw, (int, float)):
            cells[key] = float(raw)
        elif raw == "-":
            cells[key] = 0.0

    # Iteratively resolve formulas
    for _ in range(max_passes):
        changed = False
        for row in rows:
            r = row["row"]
            key = f"{col_prefix}{r}"
            formula = row.get(formula_key)
            if not formula:
                continue
            try:
                new_val = eval_formula(formula, cells)
            except FormulaError:
                continue
            old = cells.get(key)
            if old is None or abs(new_val - old) > 1e-9:
                cells[key] = new_val
                changed = True
        if not changed:
            break

    result: dict[int, float] = {}
    for row in rows:
        r = row["row"]
        key = f"{col_prefix}{r}"
        val = cells.get(key, 0.0)
        result[r] = max(0.0, float(val))
    return result
