# components/sidebar/data_tool.py

import streamlit as st
import pandas as pd
import components.state_manager as state

def render_data_tool():
    with st.expander("🛠️ Data Tool", expanded=False):

        VALID_SOURCE_KEYS = [
            "uploaded_file", "preprocessed_data", "spmf_formatted_data", "spmf_output_data"
        ]
        custom_keys = state.get_custom_data_keys()
        valid_keys = []
        for key in VALID_SOURCE_KEYS + custom_keys:
            val = state.get(key)
            if isinstance(val, pd.DataFrame):
                valid_keys.append(key)

        selected_key = st.selectbox("Select Data Source to Edit", valid_keys)
        data = state.get(selected_key)

        if data is None or not isinstance(data, pd.DataFrame):
            st.warning("Selected data is not a valid DataFrame.")
            return

        df = data.copy()

        with st.container():
            use_column_filter = st.checkbox("Enable Column Filter", key="enable_col_filter")
            if use_column_filter:
                columns_to_keep = st.multiselect("Select Columns to Keep", df.columns.tolist(), default=df.columns.tolist())
                df = df[columns_to_keep]

        if df.empty or len(df.columns) == 0:
            st.error("No columns remain in the DataFrame. Please check your filters.")
            return

        with st.container():
            use_row_filter = st.checkbox("Enable Row Filter", key="enable_row_filter")
            if use_row_filter:
                numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
                if numeric_cols:
                    filter_col = st.selectbox("Filter Column", numeric_cols)
                    filter_op = st.selectbox("Filter Operation", [">", ">=", "<", "<=", "==", "!="])
                    filter_val = st.number_input("Compare to Value", value=0.0)
                    try:
                        if filter_op == ">":
                            df = df[df[filter_col] > filter_val]
                        elif filter_op == ">=":
                            df = df[df[filter_col] >= filter_val]
                        elif filter_op == "<":
                            df = df[df[filter_col] < filter_val]
                        elif filter_op == "<=":
                            df = df[df[filter_col] <= filter_val]
                        elif filter_op == "==":
                            df = df[df[filter_col] == filter_val]
                        elif filter_op == "!=":
                            df = df[df[filter_col] != filter_val]
                    except:
                        st.warning("Filter condition failed.")
                else:
                    st.info("No numeric columns available for filtering.")

        with st.container():
            use_sorting = st.checkbox("Enable Sorting", key="enable_sorting")
            if use_sorting:
                sort_col = st.selectbox("Sort by Column", df.columns)
                sort_dir = st.radio("Direction", ["Ascending", "Descending"], horizontal=True)
                try:
                    df = df.sort_values(by=sort_col, ascending=(sort_dir == "Ascending"))
                except:
                    st.warning("Sorting failed.")

        with st.container():
            use_rename = st.checkbox("Enable Column Renaming", key="enable_rename")
            if use_rename:
                rename_df = pd.DataFrame({
                    "original": df.columns,
                    "new_name": df.columns
                })
                edited = st.data_editor(
                    rename_df,
                    column_config={
                        "original": st.column_config.Column("Original", disabled=True),
                        "new_name": st.column_config.TextColumn("New Name")
                    },
                    use_container_width=True,
                    hide_index=True,
                    key="rename_editor"
                )
                renamed = {row["original"]: row["new_name"] for _, row in edited.iterrows()}
                df = df.rename(columns=renamed)

        with st.container():
            use_datetime = st.checkbox("Enable DateTime Extraction", key="enable_dt")
            if use_datetime:
                datetime_candidates = [col for col in df.columns if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_datetime64_any_dtype(df[col])]
                if datetime_candidates:
                    time_col = st.selectbox("Date Column", datetime_candidates)
                    if st.button("Extract Year / Month / Day / Weekday"):
                        try:
                            df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
                            df[f"{time_col}_year"] = df[time_col].dt.year
                            df[f"{time_col}_month"] = df[time_col].dt.month
                            df[f"{time_col}_day"] = df[time_col].dt.day
                            df[f"{time_col}_weekday"] = df[time_col].dt.day_name()
                            st.success("Datetime components extracted.")
                        except:
                            st.error("Failed to convert to datetime.")
                else:
                    st.info("No suitable column for datetime extraction.")

        with st.container():
            use_dedup = st.checkbox("Enable Duplicate Removal", key="enable_dedupe")
            if use_dedup:
                df = df.drop_duplicates()

        with st.container():
            use_null_filter = st.checkbox("Enable Null Value Removal", key="enable_nulls")
            if use_null_filter:
                df = df.dropna()

        #  Save Result
        st.markdown("###  Save Result")
        save_as = st.text_input("Save as (Custom Name)", value="my_data")

        if st.button("Save Processed Data"):
            state.set(save_as, df)
            state.add_custom_data_key(save_as)

            windows = state.get("dashboard_windows")
            new_window = {
                "id": f"table_custom_{len(windows)+1}",
                "title": f"Custom Table: {save_as}",
                "type": "chart_table",
                "width": 6,
                "data_key": save_as
            }
            windows.append(new_window)
            state.set("dashboard_windows", windows)

            st.success(f"Saved as `{save_as}` and added to dashboard.")

