import pandas as pd
import numpy as np
from datetime import datetime
import tempfile
import components.state_manager as state

BLOCK_SIZE = 100

def parse_time(df):
    df['date_and_time'] = pd.to_datetime(df['date_and_time'], errors='coerce')
    df['dategroup'] = df['date_and_time'].dt.strftime('%Y%m%d')
    return df

def convert_spmf_file_to_dataframe(spmf_file_path):
    rows = []
    with open(spmf_file_path, "r", encoding="utf-8") as f:
        for seq_id, line in enumerate(f, start=1):
            parts = line.strip().split("-2")[0].strip()
            itemsets = parts.split(" -1 ")
            row_data = {"Sequence ID": seq_id}

            for idx, itemset in enumerate(itemsets):
                if itemset.strip() == "":
                    continue

                items = itemset.strip().split()
                row_data[f"Itemset {idx + 1}"] = ", ".join(items)

            rows.append(row_data)

    df = pd.DataFrame(rows)
    return df

def convert_to_spmf_format():
    df = state.get("preprocessed_data")

    if df is None:
        return None, None, None

    df = df.copy()

    if "date_and_time" not in df.columns or "zip_code" not in df.columns:
        raise ValueError("Missing required columns 'Date and Time' or 'Zip Code'")

    df = df.dropna(subset=["date_and_time", "zip_code"])

    df = parse_time(df)
    df["groupid"] = df["zip_code"].astype(str) + "_" + df["dategroup"]

    # Discretize
    df["vehiclecountbin"] = pd.cut(
        df["number_of_motor_vehicles"],
        bins=[-1, 1, 2, df["number_of_motor_vehicles"].max()],
        labels=["V1", "V2", "V>=3"]
    ).astype(str)

    df["injuryflag"] = df["number_of_injuries"].apply(lambda x: "Injured" if x > 0 else "NoInjury")
    df["fatalityflag"] = df["number_of_fatalities"].apply(lambda x: "Fatal" if x > 0 else "NonFatal")

    item_columns = [
        "weather_description",
        "illumination_description",
        "collision_type_description",
        "property_damage",
        "hit_and_run",
        "vehiclecountbin",
        "injuryflag",
        "fatalityflag"
    ]

    df = df.dropna(subset=item_columns)

    offsets = {col: (i + 1) * BLOCK_SIZE for i, col in enumerate(item_columns)}
    item2id = {}

    # --- 生成字典 (保存到 DataFrame)
    dict_data = []

    for col in item_columns:
        unique_vals = sorted(df[col].unique())
        base = offsets[col]
        for idx, val in enumerate(unique_vals):
            id_val = base + idx
            item2id[(col, val)] = id_val
            dict_data.append({"Column": col, "Value": val, "ID": id_val})

    dict_df = pd.DataFrame(dict_data)

    # --- 生成SPMF文件 (保存为临时文件)
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
    spmf_file_path = tmp_file.name

    with tmp_file as seq_file:
        for group, subdf in df.groupby("groupid"):
            subdf = subdf.sort_values("date_and_time")
            itemset_list = []
            for _, row in subdf.iterrows():
                ids = [str(item2id[(col, row[col])]) for col in item_columns]
                itemset_list.append(" ".join(ids))

            # 正确写法：Itemset之间加 -1，末尾加 -2
            seq_file.write(" -1 ".join(itemset_list) + " -2\n")

    # --- 转换成DataFrame格式（供可视化）
    spmf_df = convert_spmf_file_to_dataframe(spmf_file_path)

    # --- 保存到状态
    state.set("spmf_formatted_file", spmf_file_path)
    state.set("spmf_dictionary", dict_df)
    state.set("spmf_formatted_data", spmf_df)

    return spmf_file_path, dict_df, spmf_df
