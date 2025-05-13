# components/sidebar/data_tool.py

import streamlit as st
import pandas as pd
import components.state_manager as state
import components.data_ops as ops

def render_data_tool():
    with st.expander("🛠️ Data Tool", expanded=False):
        base_df = state.get("base_data")
        if base_df is None or not isinstance(base_df, pd.DataFrame):
            st.warning("Please upload and load base data first.")
            return

        tabs = st.tabs(["Normal Data Preprocessing", "SPMF Data Management"])

        # —— Normal Data Preprocessing —— #
        with tabs[0]:
            st.markdown("#### Normal Data Cleaning and Transformation")
            df = base_df.copy()

            if st.checkbox("Standardize column names", value=True):
                df = ops.standardize_columns(df)
            if st.checkbox("Drop pseudo-empty rows"):
                thresh = st.slider("Pseudo-empty row threshold", 0.0, 1.0, 0.8)
                df = ops.drop_pseudo_empty(df, threshold=thresh)
            if st.checkbox("Fill missing values"):
                id_cols = st.multiselect("ID columns", df.columns.tolist(), default=[])
                coord_cols = st.multiselect("Coordinate columns", df.columns.tolist(), default=[])
                df = ops.fill_missing(df, id_cols=id_cols, coord_cols=coord_cols)
            if st.checkbox("Extract datetime components"):
                dt_candidates = [
                    c for c in df.columns
                    if df[c].dtype == object or pd.api.types.is_datetime64_any_dtype(df[c])
                ]
                dt_col = st.selectbox("Datetime column", dt_candidates)
                df = ops.extract_datetime_components(df, dt_col)
            if st.checkbox("Drop duplicates"):
                df = ops.drop_duplicates(df)
            if st.checkbox("Drop rows with nulls"):
                df = ops.drop_nulls(df)
            if st.checkbox("Rename columns"):
                rename_map = {}
                for col in df.columns:
                    new_name = st.text_input(f"New name for {col}", value=col, key=f"rename_{col}")
                    if new_name and new_name != col:
                        rename_map[col] = new_name
                if rename_map:
                    df = ops.rename_columns(df, rename_map)

            st.markdown("**Preview cleaned data (first 10 rows)**")
            st.dataframe(df.head(10))

            save_key = st.text_input("Save as (dynamic data key)", value="cleaned_v1")
            if st.button("Save normal data version"):
                state.set(save_key, df)
                state.add_dynamic_data_key(save_key, category="normal")
                st.success(f"Saved and registered data source: `{save_key}`")

        # —— SPMF Data Management —— #
        with tabs[1]:
            st.markdown("#### SPMF Data Configuration and Generation")
            dynamic = state.get_dynamic_data_keys()
            normal_keys = [e["key"] for e in dynamic if e["category"] == "normal"]
            base_key = st.selectbox("Select normal data version", normal_keys)
            base_df = state.get(base_key)
            if base_df is None:
                st.warning("Selected data does not exist.")
                return

            dt_cols = [
                c for c in base_df.columns
                if base_df[c].dtype == object or pd.api.types.is_datetime64_any_dtype(base_df[c])
            ]
            dt_col = st.selectbox("Datetime column", dt_cols, key="spmf_dt")
            fmt = st.text_input("Datetime format", value="%m/%d/%Y %I:%M:%S %p")
            group_col = st.text_input("Group by column (e.g., zip_code)", value="zip_code")

            st.markdown("##### Select fields to include in mining")
            item_cols = st.multiselect(
                "Field list",
                base_df.columns.tolist(),
                default=[
                    "weather_description",
                    "illumination_description",
                    "collision_type_description",
                    "property_damage",
                    "hit_and_run"
                ]
            )

            # Numeric field binning configuration
            bins_config = {}
            for col in item_cols:
                if pd.api.types.is_numeric_dtype(base_df[col]):
                    st.markdown(f"###### Numeric field binning: {col}")
                    bins = st.text_input(f"{col} bins (comma-separated)", value="0,1,2,10", key=f"bins_{col}")
                    labels = st.text_input(f"{col} labels (comma-separated)", value="V0,V1,V2", key=f"labels_{col}")
                    bins = [float(x) for x in bins.split(",") if x.strip()]
                    labels = [x.strip() for x in labels.split(",") if x.strip()]
                    bins_config[col] = {"bins": bins, "labels": labels}

            if st.button("Preview dictionary & sample sequences"):
                df2 = ops.parse_time_for_spmf(base_df, datetime_col=dt_col, fmt=fmt)
                df2["groupid"] = df2[group_col].astype(str) + "_" + df2["dategroup"]
                df3 = ops.discretize_fields(df2, bins_config) if bins_config else df2
                dict_df, item2id = ops.build_spmf_dictionary(df3, item_cols)
                st.dataframe(dict_df.head(10))
                temp_path = ops.write_spmf_file(df3, item_cols, item2id)
                spmf_df = ops.spmf_to_dataframe(temp_path)
                st.dataframe(spmf_df.head(10))

            spmf_version = st.text_input("SPMF version name", value="spmf_v1", key="spmf_version")
            if st.button("Save SPMF version"):
                df2 = ops.parse_time_for_spmf(base_df, datetime_col=dt_col, fmt=fmt)
                df2["groupid"] = df2[group_col].astype(str) + "_" + df2["dategroup"]
                df3 = ops.discretize_fields(df2, bins_config) if bins_config else df2

                dict_df, item2id = ops.build_spmf_dictionary(df3, item_cols)
                spmf_file = ops.write_spmf_file(df3, item_cols, item2id)

                spmf_df = ops.spmf_to_dataframe(spmf_file)

                state.set(f"{spmf_version}_dict", dict_df)
                state.add_dynamic_data_key(f"{spmf_version}_dict", "spmf")
                state.set(f"{spmf_version}_file", spmf_file)
                state.add_dynamic_data_key(f"{spmf_version}_file", "spmf")
                state.set(f"{spmf_version}_df", spmf_df)
                state.add_dynamic_data_key(f"{spmf_version}_df", "spmf")

                st.success(f"Saved SPMF version: `{spmf_version}`")