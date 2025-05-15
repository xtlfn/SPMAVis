# components/data_ops.py

import pandas as pd
import numpy as np
import tempfile
from collections import defaultdict

def load_csv(path):
    return pd.read_csv(path)

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df

EMPTY = {"n/a", "unknown", "", " "}
def is_pseudo_empty(row, threshold=0.8):
    empty = sum(1 for v in row if pd.isna(v) or (isinstance(v, str) and v.strip().lower() in EMPTY))
    return (empty/len(row)) >= threshold

def drop_pseudo_empty(df: pd.DataFrame, threshold=0.8) -> pd.DataFrame:
    return df[~df.apply(is_pseudo_empty, axis=1)].copy()

def fill_missing_custom(df: pd.DataFrame, fill_map: dict) -> pd.DataFrame:
    df = df.copy()
    for col, val in fill_map.items():
        if col in df:
            df[col] = df[col].fillna(val)
    return df

def fill_missing_by_type(df: pd.DataFrame, type_map: dict) -> pd.DataFrame:
    df = df.copy()
    fill_map = {}
    for col, t in type_map.items():
        if t == "ID":
            fill_map[col] = "N/A"
        elif t == "Category":
            fill_map[col] = "Unknown"
        elif t == "Numeric":
            fill_map[col] = 0
        elif t == "Bool":
            fill_map[col] = False
        elif t == "Datetime":
            fill_map[col] = pd.NaT
    return fill_missing_custom(df, fill_map)

def infer_column_types(df: pd.DataFrame, sample_n: int = 1000, thresh: float = 0.8) -> dict:
    sample = df.head(sample_n)
    n = len(sample)
    types = {}
    for col in df.columns:
        s = sample[col].dropna()
        # datetime?
        dt_ok = s.map(lambda x: pd.to_datetime(x, format="%m/%d/%Y %I:%M:%S %p", errors="coerce")).notna().sum()
        if dt_ok >= thresh*n:
            types[col] = "Datetime"; continue
        # bool?
        if set(s.unique()) <= {True, False, "Y", "N"}:
            types[col] = "Bool"; continue
        # numeric?
        num_ok = s.map(lambda x: _is_float(x)).sum()
        if num_ok >= thresh*n:
            types[col] = "Numeric"; continue
        types[col] = None
    return types

def _is_float(x):
    try:
        float(x)
        return True
    except:
        return False

def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates()

def drop_nulls(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna()

def parse_time_for_spmf(df: pd.DataFrame, datetime_col="date_and_time", fmt="%m/%d/%Y %I:%M:%S %p") -> pd.DataFrame:
    df = df.copy()
    df[datetime_col] = pd.to_datetime(df[datetime_col], format=fmt, errors="coerce")
    df["dategroup"] = df[datetime_col].dt.strftime("%Y%m%d")
    return df

def discretize_fields(df: pd.DataFrame, bins_config: dict) -> pd.DataFrame:
    df = df.copy()
    for col, cfg in bins_config.items():
        df[f"{col}_bin"] = pd.cut(df[col], bins=cfg["bins"], labels=cfg["labels"]).astype(str)
    return df

def build_spmf_dictionary(df: pd.DataFrame, item_cols: list, block_size=100):
    offsets = {c:(i+1)*block_size for i,c in enumerate(item_cols)}
    item2id, data = {}, []
    for c in item_cols:
        for idx, v in enumerate(sorted(df[c].unique())):
            iid = offsets[c] + idx
            item2id[(c,v)] = iid
            data.append({"Column":c, "Value":v, "ID":iid})
    return pd.DataFrame(data), item2id

def write_spmf_file(df: pd.DataFrame, item_cols: list, item2id: dict) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
    path = tmp.name
    with tmp as f:
        for _,grp in df.groupby("groupid"):
            seqs = []
            for _,row in grp.iterrows():
                ids = [str(item2id[(c,row[c])]) for c in item_cols if (c,row[c]) in item2id]
                if ids: seqs.append(" ".join(ids))
            if seqs:
                f.write(" -1 ".join(seqs)+" -2\n")
    return path

def spmf_to_dataframe(path: str) -> pd.DataFrame:
    rows=[]
    with open(path,"r",encoding="utf-8") as f:
        for sid,line in enumerate(f,1):
            parts = line.strip().split(" -2")[0].split(" -1 ")
            d={"Sequence ID":sid}
            for i,p in enumerate(parts):
                d[f"Itemset {i+1}"]=p
            rows.append(d)
    return pd.DataFrame(rows)
