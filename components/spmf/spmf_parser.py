# components/spmf/spmf_parser.py
import pandas as pd


def parse_sequence_output(file_path: str) -> pd.DataFrame:
    rows = []
    with open(file_path, "r", encoding="utf-8") as f:
        for pid, line in enumerate(f, 1):
            parts = line.strip().split(" -1 ")
            row = {"Pattern ID": pid}

            # support (if present)
            if parts[-1].startswith("#SUP:"):
                row["Support"] = int(parts.pop(-1).replace("#SUP:", "").strip())
            else:
                row["Support"] = None

            for idx, itemset in enumerate(parts):
                if itemset.strip():
                    row[f"Itemset {idx + 1}"] = ", ".join(itemset.strip().split())

            rows.append(row)
    return pd.DataFrame(rows)


def parse_rule_output(file_path: str, dict_df: pd.DataFrame) -> pd.DataFrame:
    id_info = dict_df.set_index("ID")[["Column", "Value"]].to_dict("index")

    rows = []
    with open(file_path, "r", encoding="utf-8") as f:
        for rid, line in enumerate(f, 1):
            lhs, rhs_sup = line.split(" ==> ")
            rhs, sup_conf = rhs_sup.split(" #SUP: ")
            sup_txt, conf_txt = sup_conf.replace("#CONF:", "").split()

            def _ids_to_str(token: str):
                return " & ".join(
                    f"{id_info[int(i)]['Column']}={id_info[int(i)]['Value']}"
                    if int(i) in id_info else i
                    for i in token.strip().split()
                )

            rows.append({
                "Rule ID": rid,
                "Antecedent": _ids_to_str(lhs),
                "Consequent": _ids_to_str(rhs),
                "Support": int(sup_txt),
                "Confidence": float(conf_txt)
            })
    return pd.DataFrame(rows)


def sequence_to_readable(seq_df: pd.DataFrame, dict_df: pd.DataFrame) -> pd.DataFrame:
    id_info = dict_df.set_index("ID")[["Column", "Value"]].to_dict("index")
    patterns = []
    for _, row in seq_df.iterrows():
        pat = {"Pattern ID": row["Pattern ID"], "Support": row.get("Support")}
        parts = []
        idx = 1
        while f"Itemset {idx}" in row and pd.notna(row[f"Itemset {idx}"]):
            ids = [int(j.strip()) for j in row[f"Itemset {idx}"].split(",")]
            items = [
                f"{id_info[j]['Column']}={id_info[j]['Value']}" if j in id_info else str(j)
                for j in ids
            ]
            parts.append(" + ".join(items))
            idx += 1
        pat["Pattern"] = " → ".join(parts)
        pat["Length"] = len(parts)
        patterns.append(pat)
    return pd.DataFrame(patterns)


def parse_spmf_output(result_df: pd.DataFrame, dict_df: pd.DataFrame):
    readable_df = sequence_to_readable(result_df, dict_df)
    # rebuild old 'patterns' list of dicts
    patterns = []
    for _, row in readable_df.iterrows():
        pattern = {
            "id": row["Pattern ID"],
            "support": row["Support"],
            "sequence": [
                itemset.split(" + ")
                for itemset in row["Pattern"].split(" → ")
            ],
        }
        patterns.append(pattern)
    return patterns


def parse_to_dataframe(patterns):
    rows = []
    for p in patterns:
        rows.append(
            {
                "Pattern ID": p["id"],
                "Support": p.get("support"),
                "Length": len(p["sequence"]),
                "Pattern": " → ".join(" + ".join(it) for it in p["sequence"]),
            }
        )
    return pd.DataFrame(rows)