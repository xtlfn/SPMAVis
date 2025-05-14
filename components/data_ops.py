# components/data_ops.py

import pandas as pd
import numpy as np
import tempfile
from collections import defaultdict

# —— Basic DataFrame Operations —— #

def load_csv(file_path):
    return pd.read_csv(file_path)

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df

EMPTY_LIKE = {"n/a", "unknown", "", " "}

def is_pseudo_empty(row, threshold=0.8):
    total = len(row)
    empty = sum(
        1
        for val in row
        if pd.isna(val) or (isinstance(val, str) and val.strip().lower() in EMPTY_LIKE)
    )
    return (empty / total) >= threshold

def drop_pseudo_empty(df: pd.DataFrame, threshold=0.8) -> pd.DataFrame:
    mask = df.apply(is_pseudo_empty, axis=1)
    return df[~mask].copy()

def fill_missing(df: pd.DataFrame, id_cols=None, coord_cols=None) -> pd.DataFrame:
    df = df.copy()
    id_cols = id_cols or []
    coord_cols = coord_cols or []
    for col in df.columns:
        if col in coord_cols:
            df[col] = df[col].fillna(0.0)
        elif col in id_cols:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(np.nan)
            else:
                df[col] = df[col].fillna("N/A")
        elif df[col].dtype == object:
            df[col] = df[col].fillna("Unknown")
    return df

def extract_datetime_components(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df = df.copy()
    df[col] = pd.to_datetime(df[col], errors="coerce")
    df[f"{col}_year"] = df[col].dt.year
    df[f"{col}_month"] = df[col].dt.month
    df[f"{col}_day"] = df[col].dt.day
    df[f"{col}_weekday"] = df[col].dt.day_name()
    return df

def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates()

def drop_nulls(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna()

def rename_columns(df: pd.DataFrame, rename_map: dict) -> pd.DataFrame:
    return df.rename(columns=rename_map)


# —— SPMF-Related Conversions —— #

def parse_time_for_spmf(
    df: pd.DataFrame,
    datetime_col="date_and_time",
    fmt="%m/%d/%Y %I:%M:%S %p",
) -> pd.DataFrame:
    df = df.copy()
    df[datetime_col] = pd.to_datetime(df[datetime_col], format=fmt, errors="coerce")
    df["dategroup"] = df[datetime_col].dt.strftime("%Y%m%d")
    return df

def discretize_fields(df: pd.DataFrame, bins_config: dict) -> pd.DataFrame:
    df = df.copy()
    for col, config in bins_config.items():
        bins = config.get("bins")
        labels = config.get("labels")
        df[f"{col}_bin"] = pd.cut(df[col], bins=bins, labels=labels).astype(str)
    return df

def build_spmf_dictionary(
    df: pd.DataFrame, item_columns: list, block_size=100
):
    offsets = {col: (i + 1) * block_size for i, col in enumerate(item_columns)}
    item2id = {}
    dict_data = []
    for col in item_columns:
        unique_vals = sorted(df[col].unique())
        base = offsets[col]
        for idx, val in enumerate(unique_vals):
            id_val = base + idx
            item2id[(col, val)] = id_val
            dict_data.append({"Column": col, "Value": val, "ID": id_val})
    dict_df = pd.DataFrame(dict_data)
    return dict_df, item2id

def write_spmf_file(
    df: pd.DataFrame, item_columns: list, item2id: dict
) -> str:
    tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix=".txt", mode="w", encoding="utf-8"
    )
    path = tmp.name
    with tmp as f:
        for _, group in df.groupby("groupid"):
            group = group.sort_values("date_and_time")
            seq_itemsets = []
            for _, row in group.iterrows():
                ids = []
                for col in item_columns:
                    key = (col, row[col])
                    if key in item2id:
                        ids.append(str(item2id[key]))
                if ids:
                    seq_itemsets.append(" ".join(ids))
            if seq_itemsets:
                f.write(" -1 ".join(seq_itemsets) + " -2\n")
    return path

def spmf_to_dataframe(spmf_file_path: str) -> pd.DataFrame:
    rows = []
    with open(spmf_file_path, "r", encoding="utf-8") as f:
        for seq_id, line in enumerate(f, start=1):
            parts = line.strip().split("-2")[0].strip()
            itemsets = parts.split(" -1 ")
            row_data = {"Sequence ID": seq_id}
            for idx, itemset in enumerate(itemsets):
                if itemset.strip():
                    items = itemset.strip().split()
                    row_data[f"Itemset {idx+1}"] = ", ".join(items)
            rows.append(row_data)
    return pd.DataFrame(rows)
