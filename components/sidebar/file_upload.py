# components/sidebar/file_upload.py

import streamlit as st
import pandas as pd
import numpy as np
import components.state_manager as state

# 识别编号类字段
ID_KEYWORDS = ["id", "number", "code", "zip", "objectid"]

def is_id_column(col_name):
    col_lower = col_name.lower()
    return any(keyword in col_lower for keyword in ID_KEYWORDS)

# 识别坐标类字段
def is_coordinate_column(col_name):
    col_lower = col_name.lower()
    return "lat" in col_lower or "long" in col_lower or col_lower in ["x", "y"]

# 判断伪空行（空、N/A、Unknown等占比高的行）
def is_pseudo_empty(row, threshold=0.8):
    empty_like = ["n/a", "unknown", "", " "]
    total = len(row)
    empty_count = 0

    for val in row:
        if pd.isna(val):
            empty_count += 1
        elif isinstance(val, str) and val.strip().lower() in empty_like:
            empty_count += 1

    return (empty_count / total) >= threshold

# 移除伪空行
def remove_pseudo_empty_rows(df, threshold=0.8):
    before = len(df)
    mask = df.apply(is_pseudo_empty, axis=1)
    df_cleaned = df[~mask].copy()
    after = len(df_cleaned)

    st.write(f"Removed {before - after} pseudo-empty rows.")
    return df_cleaned

def render_file_upload():

    with st.expander("📁 File Upload", expanded=False):
        st.header("Upload Raw Dataset")

        uploaded_file = st.file_uploader("Select File", type=["csv", "txt"])

        if uploaded_file:
            st.write(f"**Uploaded File:** {uploaded_file.name}")

        st.subheader("Pre-processing Options")

        standardize_column_names = st.checkbox("Standardize Column Names (lowercase, remove spaces)", value=True)
        remove_empty_rows = st.checkbox("Remove Empty Rows (All or Mostly Empty Rows)", value=True)
        auto_add_dashboard = st.checkbox("Auto Add to Dashboard (Table)", value=True)

        if st.button("Load and Preprocess") and uploaded_file:

            # Load raw data
            df_raw = pd.read_csv(uploaded_file)
            state.set("uploaded_file", df_raw)

            # Processing copy
            df = df_raw.copy()

            # Standardize column names
            if standardize_column_names:
                df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

            # Remove pseudo empty rows FIRST (before filling)
            if remove_empty_rows:
                df = remove_pseudo_empty_rows(df)

            # 填补空值（仅分类、ID、坐标填，数值保持np.nan不填N/A，保证数据干净）
            for col in df.columns:
                if is_coordinate_column(col):
                    df[col] = df[col].fillna(0.0)
                elif is_id_column(col):
                    if pd.api.types.is_numeric_dtype(df[col]):
                        df[col] = df[col].fillna(np.nan)
                    else:
                        df[col] = df[col].fillna("N/A")
                elif df[col].dtype == object:
                    df[col] = df[col].fillna("Unknown")

            # 最后统一转换数据类型，保证没有object混杂
            df = df.convert_dtypes()

            # Save preprocessed data
            state.set("preprocessed_data", df)

            st.success("File loaded and preprocessed successfully!")

            if auto_add_dashboard:
                windows = state.get("dashboard_windows")

                new_window = {
                    "id": f"table_auto_{len(windows)+1}",
                    "title": f"Table View: {uploaded_file.name}",
                    "type": "chart_table",
                    "width": 6,
                    "data_key": "preprocessed_data"
                }

                windows.append(new_window)
                state.set("dashboard_windows", windows)

                st.success("Added to dashboard!")
