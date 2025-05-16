# components/sidebar/data_tool.py

import streamlit as st
import pandas as pd
import components.state_manager as state
import components.data_ops as ops

def render_data_tool():
    state.init_state()
    df_base = state.get("base_data")
    if df_base is None or not isinstance(df_base, pd.DataFrame):
        with st.expander("🛠️ Data Tool"):
            st.warning("Please upload and load base data first.")
        return

    df_base = ops.standardize_columns(df_base)
    init_map = ops.infer_column_types(df_base)

    with st.expander("🛠️ Data Tool", expanded=False):
        tabs = st.tabs(["Types", "Clean", "SPMF"])

        # Types Tab
        with tabs[0]:
            cols      = df_base.columns.tolist()
            id_cols   = st.multiselect("ID columns", cols, default=[c for c in ["objectid","accident_number"] if c in cols])
            cat_cols  = st.multiselect("Category columns", cols, default=[c for c in cols if c not in id_cols])
            num_cols  = st.multiselect("Numeric columns", cols, default=[c for c,t in init_map.items() if t=="Numeric"])
            dt_cols   = st.multiselect("Datetime columns", cols, default=[c for c,t in init_map.items() if t=="Datetime"])
            bool_cols = st.multiselect("Bool columns", cols, default=[c for c,t in init_map.items() if t=="Bool"])
            type_map  = {c:"Numeric"  for c in num_cols}
            type_map.update({c:"Datetime" for c in dt_cols})
            type_map.update({c:"Bool"     for c in bool_cols})
            type_map.update({c:"ID"       for c in id_cols})
            type_map.update({c:"Category" for c in cat_cols})
            st.session_state["col_types"] = type_map

        # Clean Tab
        with tabs[1]:
            df = df_base.copy()
            type_map = st.session_state["col_types"]

            drop_pe    = st.checkbox("Drop pseudo-empty rows", key="drop_pe")
            if drop_pe:
                pe_thresh = st.slider("PE threshold", 0.0, 1.0, 0.8, key="pe_thresh")

            fill_type  = st.checkbox("Fill missing by type", key="fill_type")

            select_cols = st.checkbox("Select columns", key="select_cols")
            if select_cols:
                keep_cols = st.multiselect("Columns to keep", df.columns.tolist(), default=df.columns.tolist(), key="keep_cols")

            filter_rows = st.checkbox("Filter rows", key="filter_rows")
            if filter_rows:
                fc = st.selectbox("Filter column", df.columns.tolist(), key="filter_col")
                op = st.selectbox("Operator", [">",">=","<","<=","==","!="], key="filter_op")
                val= st.text_input("Filter value", key="filter_val")

            drop_dup  = st.checkbox("Drop duplicates", key="drop_dup")

            # new: choose which values to treat as null
            drop_null = st.checkbox("Drop null rows", key="drop_null")
            if drop_null:
                null_types = st.multiselect(
                    "Null value types to drop",
                    options=["NaN", "UNKNOWN"],
                    default=["NaN"],
                    key="null_types"
                )
                custom_nulls = st.text_input(
                    "Custom null values (comma-separated)",
                    value="",
                    key="custom_nulls"
                )

            save_key  = st.text_input("Save key", "cleaned_v1", key="save_clean_key")

            if st.button("Preview clean"):
                df2 = df.copy()
                if drop_pe:
                    df2 = ops.drop_pseudo_empty(df2, threshold=pe_thresh)
                if fill_type:
                    df2 = ops.fill_missing_by_type(df2, type_map)

                # enforce types
                for col,t in type_map.items():
                    if t=="Datetime":
                        df2[col] = pd.to_datetime(df2[col], format="%m/%d/%Y %I:%M:%S %p", errors="coerce")
                    elif t=="Bool":
                        df2[col] = df2[col].map(lambda x: True if str(x).upper()=="Y" else False).astype("boolean")
                    elif t in ("Category","ID"):
                        df2[col] = df2[col].astype("string")

                if select_cols:
                    df2 = df2[keep_cols]
                if filter_rows:
                    try:
                        cv = float(val) if op in [">",">=","<","<="] else val
                        df2 = df2.query(f"`{fc}` {op} @cv")
                    except:
                        st.warning("Filter failed")
                if drop_dup:
                    df2 = ops.drop_duplicates(df2)

                if drop_null:
                    # replace selected as NA then drop
                    vals = []
                    if "NaN" in null_types:
                        vals.append(pd.NA)
                    if "UNKNOWN" in null_types:
                        vals.append("UNKNOWN")
                    vals += [x.strip() for x in custom_nulls.split(",") if x.strip()]
                    df2 = df2.replace(vals, pd.NA)
                    df2 = ops.drop_nulls(df2)

                st.session_state["preview_df"] = df2
                st.dataframe(df2.head(10))

            if st.button("Save clean"):
                df2 = st.session_state.get("preview_df")
                if df2 is None:
                    st.warning("Please click Preview clean first")
                else:
                    state.set(save_key, df2)
                    state.add_dynamic_data_key(save_key, "normal")
                    st.success(f"Cleaned data saved as `{save_key}`")

        # SPMF Tab
        with tabs[2]:
            dyn         = state.get_dynamic_data_keys()
            normal_keys = [e["key"] for e in dyn if e["category"]=="normal"]
            df0         = None

            base_key    = st.selectbox("Base data", normal_keys, key="spmf_base")
            df0         = state.get(base_key)
            type_map    = st.session_state["col_types"]
            dt_opts     = [c for c,t in type_map.items() if t=="Datetime"]
            dt_col      = st.selectbox("Datetime column", dt_opts, key="spmf_dt")
            fmt         = st.text_input("Datetime format", "%m/%d/%Y %I:%M:%S %p", key="spmf_fmt")
            grp         = st.text_input("Group by column", "zip_code", key="spmf_grp")
            fields      = st.multiselect("Fields", df0.columns.tolist() if df0 is not None else [], key="spmf_fields")

            bins_conf = {}
            for c in fields:
                if type_map.get(c) == "Numeric":
                    b = st.text_input(f"{c} bins", "0,1,2,10", key=f"bins_{c}")
                    l = st.text_input(f"{c} labels", "V0,V1,V2", key=f"labels_{c}")
                    bins_conf[c] = {
                        "bins":   [float(x) for x in b.split(",") if x.strip()],
                        "labels": [x.strip()   for x in l.split(",") if x.strip()]
                    }

            save_spmf_key   = st.text_input("SPMF save key", "spmf_v1", key="spmf_save_key")
            if st.button("Preview SPMF"):
                d1 = ops.parse_time_for_spmf(df0, datetime_col=dt_col, fmt=fmt)
                d1["groupid"] = d1[grp].astype(str) + "_" + d1["dategroup"]
                d2 = ops.discretize_fields(d1, bins_conf) if bins_conf else d1
                d2 = d2.dropna(subset=fields)
                dict_df, it2id = ops.build_spmf_dictionary(d2, fields)
                st.dataframe(dict_df.head(10))
                tmp = ops.write_spmf_file(d2, fields, it2id)
                spdf = ops.spmf_to_dataframe(tmp)
                st.dataframe(spdf.head(10))

            if st.button("Save SPMF"):
                d1 = ops.parse_time_for_spmf(df0, datetime_col=dt_col, fmt=fmt)
                d1["groupid"] = d1[grp].astype(str) + "_" + d1["dategroup"]
                d2 = ops.discretize_fields(d1, bins_conf) if bins_conf else d1
                d2 = d2.dropna(subset=fields)
                dict_df, it2id = ops.build_spmf_dictionary(d2, fields)
                path = ops.write_spmf_file(d2, fields, it2id)
                spf  = ops.spmf_to_dataframe(path)
                state.set(f"{save_spmf_key}_dict", dict_df)
                state.add_dynamic_data_key(f"{save_spmf_key}_dict","spmf")
                state.set(f"{save_spmf_key}_file", path)
                state.add_dynamic_data_key(f"{save_spmf_key}_file","spmf")
                state.set(f"{save_spmf_key}_df", spf)
                state.add_dynamic_data_key(f"{save_spmf_key}_df","spmf")
                st.success(f"SPMF saved as `{save_spmf_key}`")
