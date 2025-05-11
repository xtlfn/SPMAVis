# components/spmf/spmf_parser.py

import pandas as pd

def parse_spmf_output(result_df: pd.DataFrame, dict_df: pd.DataFrame):
    id_to_info = dict_df.set_index("ID")[["Column", "Value"]].to_dict(orient="index")

    patterns = []
    for i, row in result_df.iterrows():
        pattern = {
            "id": row.get("Pattern ID", i + 1),
            "sequence": [],
            "support": int(row["Support"]) if "Support" in row else None
        }

        itemset_index = 1
        while f"Itemset {itemset_index}" in row:
            itemset_raw = row[f"Itemset {itemset_index}"]
            if pd.isna(itemset_raw):
                break
            ids = [int(x) for x in str(itemset_raw).split(",") if x.strip().isdigit()]
            items = []
            for item_id in ids:
                if item_id in id_to_info:
                    info = id_to_info[item_id]
                    items.append(f"{info['Column']}={info['Value']}")
                else:
                    items.append(str(item_id))
            pattern["sequence"].append(items)
            itemset_index += 1

        patterns.append(pattern)

    return patterns

def parse_to_dataframe(patterns):
    rows = []
    for p in patterns:
        row = {
            "Pattern ID": p["id"],
            "Support": p.get("support", None),
            "Length": len(p["sequence"]),
            "Pattern": " → ".join([" + ".join(itemset) for itemset in p["sequence"]])
        }
        rows.append(row)
    return pd.DataFrame(rows)