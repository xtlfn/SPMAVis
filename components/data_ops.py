# components/data_ops.py

import pandas as pd
import numpy as np
import tempfile
import os
import uuid
from collections import defaultdict

def load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df

_EMPTY_TOKENS = {"n/a", "unknown", "", " "}

def _is_pseudo_empty(row, threshold: float) -> bool:
    empty = sum(
        1
        for v in row
        if pd.isna(v) or (isinstance(v, str) and v.strip().lower() in _EMPTY_TOKENS)
    )
    return empty / len(row) >= threshold

def drop_pseudo_empty(df: pd.DataFrame, threshold: float = 0.8) -> pd.DataFrame:
    return df[~df.apply(_is_pseudo_empty, axis=1, threshold=threshold)].copy()

def fill_missing_by_type(df: pd.DataFrame, type_map: dict) -> pd.DataFrame:
    df = df.copy()
    df.replace(list(_EMPTY_TOKENS), pd.NA, inplace=True)
    for col, t in type_map.items():
        if col not in df:
            continue
        if t == "Numeric":
            df[col] = df[col].fillna(0)
        elif t == "Bool":
            df[col] = df[col].fillna(False)
        elif t in {"Category", "ID"}:
            df[col] = df[col].fillna("Unknown")
        elif t == "Datetime":
            df[col] = df[col].fillna(pd.NaT)
    return df

def _try_parse_dt(series: pd.Series, fmt: str) -> bool:
    return pd.to_datetime(series, format=fmt, errors="coerce").notna().mean() > 0.8

def infer_column_types(df: pd.DataFrame, sample_n: int = 1000) -> dict:
    sample = df.head(sample_n)
    res = {}
    for col in df.columns:
        s = sample[col].dropna()
        if s.empty:
            res[col] = None
            continue
        if _try_parse_dt(s, "%m/%d/%Y %I:%M:%S %p"):
            res[col] = "Datetime"
        elif pd.api.types.is_bool_dtype(s):
            res[col] = "Bool"
        elif pd.api.types.is_numeric_dtype(s):
            res[col] = "Numeric"
        else:
            res[col] = None
    return res

def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates()

def drop_nulls(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna()

def parse_time_for_spmf(
    df: pd.DataFrame, datetime_col: str, fmt: str = "%m/%d/%Y %I:%M:%S %p"
) -> pd.DataFrame:
    df = df.copy()
    df[datetime_col] = pd.to_datetime(df[datetime_col], format=fmt, errors="coerce")
    df["dategroup"] = df[datetime_col].dt.strftime("%Y%m%d")
    return df

def discretize_fields(df: pd.DataFrame, bins_config: dict) -> pd.DataFrame:
    df = df.copy()
    for col, cfg in bins_config.items():
        if col not in df:
            continue
        df[f"{col}_bin"] = pd.cut(
            df[col], bins=cfg["bins"], labels=cfg["labels"], include_lowest=True
        )
    return df

def build_spmf_dictionary(df: pd.DataFrame, item_cols: list):
    item2id = {}
    data = []
    next_id = 1
    for col in item_cols:
        for val in sorted(df[col].dropna().unique()):
            item2id[(col, val)] = next_id
            data.append({"Column": col, "Value": val, "ID": next_id})
            next_id += 1
    return pd.DataFrame(data), item2id

def _tmp_path() -> str:
    os.makedirs("tmp_spmf", exist_ok=True)
    return os.path.join("tmp_spmf", f"{uuid.uuid4().hex}.txt")

def write_spmf_file(
    df: pd.DataFrame, item_cols: list, item2id: dict, path: str | None = None
) -> str:
    path = path or _tmp_path()
    with open(path, "w", encoding="utf-8") as f:
        for _, grp in df.groupby("groupid"):
            seq = []
            for _, row in grp.iterrows():
                ids = [
                    str(item2id[(c, row[c])])
                    for c in item_cols
                    if (c, row[c]) in item2id
                ]
                if ids:
                    seq.append(" ".join(ids))
            if seq:
                f.write(" -1 ".join(seq) + " -2\n")
    return path

def spmf_to_dataframe(path: str) -> pd.DataFrame:
    rows = []
    with open(path, encoding="utf-8") as f:
        for sid, line in enumerate(f, 1):
            parts = line.strip().split(" -2")[0].split(" -1 ")
            row = {"Sequence ID": sid}
            row.update({f"Itemset {i+1}": p for i, p in enumerate(parts)})
            rows.append(row)
    return pd.DataFrame(rows)