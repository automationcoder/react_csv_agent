import ast
import json
import operator
from pathlib import Path
import pandas as pd

from project.tools.registry import register_tool
from project.tools.params_models import CalculatorParams, ListDataFilesParams, ReadFileParams, ReadCsvParams, AggregateCsvParams


_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.Mod: operator.mod,
}


def _safe_eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Expression contains unsupported syntax.")


@register_tool
def calculator(params: CalculatorParams) -> str:
    """Evaluate a mathematical expression exactly. Use this for arithmetic instead of asking the LLM to calculate."""
    try:
        tree = ast.parse(params.expression, mode="eval")
        return json.dumps({"ok": True, "result": _safe_eval(tree.body)}, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"ok": False, "error": f"Calculator error: {exc}"}, ensure_ascii=False)


@register_tool
def list_data_files(params: ListDataFilesParams) -> str:
    """List local uploaded data files from a folder. Use this when the user asks what files are available locally."""
    folder = Path(params.folder)
    if not folder.exists():
        return json.dumps({"ok": False, "error": f"Folder does not exist: {params.folder}"}, ensure_ascii=False)
    files = [str(p) for p in folder.iterdir() if p.is_file()]
    return json.dumps({"ok": True, "folder": str(folder), "files": files}, indent=2, ensure_ascii=False)


@register_tool
def read_file(params: ReadFileParams) -> str:
    """Read a local text file and return a limited preview. Use this for text, markdown, JSON, YAML, or small files."""
    path = Path(params.path)
    if not path.exists():
        return json.dumps({"ok": False, "error": f"File does not exist: {params.path}"}, ensure_ascii=False)
    text = path.read_text(encoding="utf-8", errors="replace")[: params.max_chars]
    return json.dumps({"ok": True, "path": str(path), "content": text}, ensure_ascii=False)


@register_tool
def read_csv(params: ReadCsvParams) -> str:
    """Describe a CSV file: rows, columns, data types, missing values, and sample rows."""
    try:
        path = Path(params.path)
        if not path.exists():
            return json.dumps({"ok": False, "error": f"CSV file does not exist: {params.path}"}, ensure_ascii=False)
        df = pd.read_csv(path)
        result = {
            "ok": True,
            "path": str(path),
            "rows": int(len(df)),
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing_values": {col: int(value) for col, value in df.isna().sum().items()},
            "sample": df.head(params.sample_rows).to_dict(orient="records"),
        }
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"ok": False, "error": f"CSV read error: {exc}"}, ensure_ascii=False)


@register_tool
def aggregate_csv(params: AggregateCsvParams) -> str:
    """Aggregate CSV data using group_by columns and aggregation functions such as sum, mean, count, min, and max."""
    try:
        path = Path(params.path)
        if not path.exists():
            return json.dumps({"ok": False, "error": f"CSV file does not exist: {params.path}"}, ensure_ascii=False)

        df = pd.read_csv(path)
        allowed = {"sum", "mean", "count", "min", "max"}

        missing_group = [col for col in params.group_by if col not in df.columns]
        if missing_group:
            return json.dumps({"ok": False, "error": f"Missing group_by columns: {missing_group}", "available_columns": list(df.columns)}, ensure_ascii=False)

        for col, fn in params.aggregations.items():
            if col not in df.columns:
                return json.dumps({"ok": False, "error": f"Missing aggregation column: {col}", "available_columns": list(df.columns)}, ensure_ascii=False)
            if fn not in allowed:
                return json.dumps({"ok": False, "error": f"Unsupported aggregation '{fn}'. Supported: {sorted(allowed)}"}, ensure_ascii=False)

        grouped = df.groupby(params.group_by, as_index=False).agg(params.aggregations)
        grouped.columns = [
            col if col in params.group_by else f"{col}_{params.aggregations[col]}"
            for col in grouped.columns
        ]
        return grouped.to_json(orient="records", force_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"ok": False, "error": f"CSV aggregation error: {exc}"}, ensure_ascii=False)
