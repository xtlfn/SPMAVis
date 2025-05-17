# components/spmf/spmf_converter.py
import pandas as pd
import numpy as np
import tempfile
from pathlib import Path
import components.state_manager as state

BLOCK_SIZE = 100


# ---------- helpers ----------------------------------------------------------
def _tmp_path(suffix: str = ".txt") -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.close()
    return tmp.name


def _parse_time(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date_and_time"] = pd.to_datetime(
        df["date_and_time"],
        format="%m/%d/%Y %I:%M:%S %p",
        errors="coerce",
    )
    df["dategroup"] = df["date_and_time"].dt.strftime("%Y%m%d")
    return df


# ---------- common dictionary builder ---------------------------------------
def build_dictionary(df: pd.DataFrame, item_cols: list[str]) -> tuple[pd.DataFrame, dict]:
    offsets = {col: (i + 1) * BLOCK_SIZE for i, col in enumerate(item_cols)}
    item2id, dict_rows = {}, []
    for col in item_cols:
        base = offsets[col]
        for idx, val in enumerate(sorted(df[col].dropna().unique())):
            iid = base + idx
            item2id[(col, val)] = iid
            dict_rows.append({"Column": col, "Value": val, "ID": iid})
    return pd.DataFrame(dict_rows), item2id


# ---------- writers ---------------------------------------------------------
def write_sequence_file(df: pd.DataFrame, item_cols: list[str], item2id: dict) -> str:
    path = _tmp_path()
    with open(path, "w", encoding="utf-8") as f:
        for _, grp in df.groupby("groupid"):
            grp = grp.sort_values("date_and_time")
            seq = [
                " ".join(
                    str(item2id[(c, v)]) for c, v in row[item_cols].items()
                    if pd.notna(v) and (c, v) in item2id
                )
                for _, row in grp.iterrows()
            ]
            f.write(" -1 ".join(seq) + " -2\n")
    return path


def write_transaction_file(df: pd.DataFrame, item_cols: list[str], item2id: dict) -> str:
    path = _tmp_path()
    with open(path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            ids = [str(item2id[(c, row[c])]) for c in item_cols if (c, row[c]) in item2id]
            if ids:
                f.write(" ".join(ids) + "\n")
    return path


# ---------- converters for UI ------------------------------------------------
def sequence_converter(df: pd.DataFrame, time_col: str, fmt: str, group_col: str, item_cols: list, bins_conf: dict):
    df = df.copy()
    df[time_col] = pd.to_datetime(df[time_col], format=fmt, errors="coerce")
    df["dategroup"] = df[time_col].dt.strftime("%Y%m%d")
    df["groupid"] = df[group_col].astype(str) + "_" + df["dategroup"]

    for c, conf in bins_conf.items():
        df[c] = pd.cut(df[c], bins=conf["bins"], labels=conf["labels"], include_lowest=True).astype(str)

    df = df.dropna(subset=item_cols)
    dict_df, item2id = build_dictionary(df, item_cols)
    file_path = write_sequence_file(df, item_cols, item2id)
    spmf_df = _sequence_to_df(file_path)
    return file_path, dict_df, spmf_df


def transaction_converter(df: pd.DataFrame, item_cols: list, bins_conf: dict):
    df = df.copy()
    for c, conf in bins_conf.items():
        df[c] = pd.cut(df[c], bins=conf["bins"], labels=conf["labels"], include_lowest=True).astype(str)

    df = df.dropna(subset=item_cols)
    dict_df, item2id = build_dictionary(df, item_cols)
    file_path = write_transaction_file(df, item_cols, item2id)
    trx_df = pd.read_csv(file_path, header=None, names=["Transaction"])
    return file_path, dict_df, trx_df


# ---------- util -------------------------------------------------------------
def _sequence_to_df(spmf_file_path: str) -> pd.DataFrame:
    rows = []
    with open(spmf_file_path, "r", encoding="utf-8") as f:
        for sid, line in enumerate(f, 1):
            parts = line.strip().split("-2")[0].strip().split(" -1 ")
            row = {"Sequence ID": sid}
            for idx, itemset in enumerate(parts):
                row[f"Itemset {idx + 1}"] = itemset.replace(" ", ", ")
            rows.append(row)
    return pd.DataFrame(rows)