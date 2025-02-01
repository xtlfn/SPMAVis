import pandas as pd
import subprocess

# Load and process input
def load_data(file_path):
    try:
        rows = []
        with open(file_path, "r") as f:
            lines = f.readlines()
        for line in lines:
            tokens = line.strip().split()
            pattern_columns = []
            current = []
            for token in tokens:
                if token == "-1":
                    if current:
                        pattern_columns.append(" ".join(current))
                        current = []
                elif token == "-2":
                    continue
                else:
                    current.append(token)
            if current:
                pattern_columns.append(" ".join(current))
            rows.append(pattern_columns)
        max_patterns = max((len(row) for row in rows), default=0)
        data = {f"Pattern {i+1}": [row[i] if i < len(row) else None for row in rows] for i in range(max_patterns)}
        return pd.DataFrame(data)
    except Exception as e:
        return f"Error reading file: {e}"

# load and process output
def load_output_data(file_path):
    try:
        rows = []
        with open(file_path, "r") as f:
            lines = f.readlines()
        for line in lines:
            fields = line.strip().split()
            if "#SUP:" in fields:
                sup_index = fields.index("#SUP:")
                support = int(fields[sup_index + 1])
                pattern_fields = fields[:sup_index]
            else:
                support = None
                pattern_fields = fields
            pattern_columns = []
            current = []
            for token in pattern_fields:
                if token == "-1":
                    if current:
                        pattern_columns.append(current)
                        current = []
                elif token == "-2":
                    continue
                else:
                    current.append(token)
            if current:
                pattern_columns.append(current)
            row_dict = {}
            if support is not None:
                row_dict["Support Count"] = support
            for i, pattern in enumerate(pattern_columns, start=1):
                row_dict[f"Pattern {i}"] = " ".join(pattern)
            rows.append(row_dict)
        max_patterns = max((len([key for key in row if key.startswith("Pattern")]) for row in rows), default=0)
        for row in rows:
            for i in range(1, max_patterns + 1):
                key = f"Pattern {i}"
                if key not in row:
                    row[key] = None
        df = pd.DataFrame(rows)
        columns_order = []
        if "Support Count" in df.columns:
            columns_order.append("Support Count")
        pattern_cols = sorted([col for col in df.columns if col.startswith("Pattern ")],
                              key=lambda x: int(x.split()[1]))
        columns_order.extend(pattern_cols)
        return df[columns_order]
    except Exception as e:
        return f"Error reading file: {e}"

# Postprocessing function 1 : Add unique items
def add_unique_items_column_from_df(df):
    try:
        pattern_cols = [col for col in df.columns if col.startswith("Pattern")]
        if not pattern_cols:
            df["Unique Items"] = 0
        else:
            def compute_unique(row):
                return len({token for col in pattern_cols 
                            for token in (row[col].split() if pd.notnull(row[col]) and row[col].strip() else [])})
            df["Unique Items"] = df.apply(compute_unique, axis=1)
        if "Support Count" in df.columns:
            pattern_sorted = sorted([col for col in df.columns if col.startswith("Pattern")],
                                    key=lambda x: int(x.split()[1]))
            other_cols = [col for col in df.columns if col not in ["Support Count", "Unique Items"] and not col.startswith("Pattern")]
            new_order = ["Support Count", "Unique Items"] + pattern_sorted + other_cols
        else:
            pattern_sorted = sorted([col for col in df.columns if col.startswith("Pattern")],
                                    key=lambda x: int(x.split()[1]))
            other_cols = [col for col in df.columns if col not in ["Unique Items"] and not col.startswith("Pattern")]
            new_order = ["Unique Items"] + pattern_sorted + other_cols
        return df[new_order]
    except Exception as e:
        return f"Error processing DataFrame for unique items: {e}"

# Run SPMF algorithm with Java
def run_spmf_command(command):
    subprocess.run(command, shell=True, capture_output=True, text=True)
