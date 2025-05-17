# components/sidebar/data_tool.py
import streamlit as st
import pandas as pd
import components.state_manager as state
import components.data_ops as ops


def _ensure_types(df: pd.DataFrame, type_map: dict) -> pd.DataFrame:
    df = df.copy()
    for col, t in type_map.items():
        if col not in df:
            continue
        if t == "Datetime":
            if not pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = pd.to_datetime(df[col], errors="coerce")
        elif t == "Bool":
            df[col] = (
                df[col]
                .astype(str)
                .str.upper()
                .map({"Y": True, "N": False, "TRUE": True, "FALSE": False})
                .astype("boolean")
            )
        elif t in {"Category", "ID"}:
            df[col] = df[col].astype("string")
    return df


def _clean_dataframe(df: pd.DataFrame, params: dict) -> pd.DataFrame:
    df2 = df.copy()
    if params["drop_pe"]:
        df2 = ops.drop_pseudo_empty(df2, params["pe_thresh"])
    if params["fill_type"]:
        df2 = ops.fill_missing_by_type(df2, params["type_map"])
    df2 = _ensure_types(df2, params["type_map"])
    if params["select_cols"]:
        df2 = df2[params["keep_cols"]]
    if params["filter_rows"]:
        fc, op, val = params["filter_col"], params["filter_op"], params["filter_val"]
        try:
            cv = float(val) if op in [">", ">=", "<", "<="] else val
            df2 = df2.query(f"`{fc}` {op} @cv")
        except Exception:
            st.warning("Filter expression failed")
    if params["drop_dup"]:
        df2 = ops.drop_duplicates(df2)
    if params["drop_null"]:
        vals = []
        if "NaN" in params["null_types"]:
            vals.append(pd.NA)
        if "UNKNOWN" in params["null_types"]:
            vals.append("UNKNOWN")
        vals += [x.strip() for x in params["custom_nulls"].split(",") if x.strip()]
        df2 = df2.replace(vals, pd.NA)
        df2 = ops.drop_nulls(df2)
    return df2


def _next_key(base: str) -> str:
    idx = 1
    while state.get(f"{base}_cleaned_v{idx}") is not None:
        idx += 1
    return f"{base}_cleaned_v{idx}"


def render_data_tool():
    state.init_state()

    base_df = state.get("base_data")
    if base_df is None or not isinstance(base_df, pd.DataFrame):
        with st.expander("🛠️ Data Tool"):
            st.warning("Please upload and load base data first.")
        return
    base_df = ops.standardize_columns(base_df)

    with st.expander("🛠️ Data Tool", expanded=False):
        # -------- Data source selector --------
        normal_keys = [e["key"] for e in state.get_dynamic_data_keys() if e["category"] == "normal"]
        source_options = ["base_data"] + normal_keys
        source_key = st.selectbox("Data source", source_options)
        df_src = base_df if source_key == "base_data" else state.get(source_key)
        if df_src is None or not isinstance(df_src, pd.DataFrame):
            st.warning("Selected data source is empty.")
            return
        df_src = ops.standardize_columns(df_src)

        if "col_types" not in st.session_state:
            st.session_state["col_types"] = ops.infer_column_types(df_src)

        tabs = st.tabs(["Types", "Clean", "SPMF"])

        # -------- Types Tab --------
        with tabs[0]:
            cols = df_src.columns.tolist()
            groups = ["ID", "Numeric", "Datetime", "Bool", "Category"]

            if "type_sel" not in st.session_state:
                inf = ops.infer_column_types(df_src)
                st.session_state.type_sel = {
                    "ID": [],
                    "Numeric": [],
                    "Datetime": [c for c, t in inf.items() if t == "Datetime"],
                    "Bool": [c for c, t in inf.items() if t == "Bool"],
                    "Category": [
                        c
                        for c in cols
                        if c not in inf or inf.get(c) is None or inf[c] not in {"Datetime", "Bool"}
                    ],
                }

            sel_prev = st.session_state.type_sel
            for k in groups:
                sel_prev.setdefault(k, [])

            assigned = set()
            sel_new = {}

            for g in groups:
                current_val = st.session_state.get(f"{g}_cols", sel_prev[g])
                options = sorted(set(cols) - assigned | set(current_val))
                defaults = [c for c in current_val if c in options]
                chosen = st.multiselect(f"{g} columns", options, defaults, key=f"{g}_cols")
                sel_new[g] = chosen
                assigned.update(chosen)

            st.session_state.type_sel = sel_new

            tm = {c: "ID" for c in sel_new["ID"]}
            tm.update({c: "Numeric" for c in sel_new["Numeric"]})
            tm.update({c: "Datetime" for c in sel_new["Datetime"]})
            tm.update({c: "Bool" for c in sel_new["Bool"]})
            tm.update({c: "Category" for c in sel_new["Category"]})
            st.session_state["col_types"] = tm

        # -------- Clean Tab --------
        with tabs[1]:
            tm = st.session_state["col_types"]
            drop_pe = st.checkbox("Drop pseudo-empty rows", key="drop_pe")
            pe_thresh = st.slider("PE threshold", 0.0, 1.0, 0.8) if drop_pe else 0.8
            fill_type = st.checkbox("Fill missing by type", key="fill_type")
            select_cols = st.checkbox("Select columns", key="select_cols")
            keep_cols = (
                st.multiselect("Columns to keep", df_src.columns.tolist(), default=df_src.columns.tolist())
                if select_cols
                else df_src.columns.tolist()
            )
            filter_rows = st.checkbox("Filter rows", key="filter_rows")
            filter_col, filter_op, filter_val = None, None, None
            if filter_rows:
                filter_col = st.selectbox("Filter column", df_src.columns.tolist())
                filter_op = st.selectbox("Operator", [">", ">=", "<", "<=", "==", "!="])
                filter_val = st.text_input("Filter value")
            drop_dup = st.checkbox("Drop duplicates", key="drop_dup")
            drop_null = st.checkbox("Drop null rows", key="drop_null")
            null_types = (
                st.multiselect("Null value types", ["NaN", "UNKNOWN"], default=["NaN"])
                if drop_null
                else []
            )
            custom_nulls = st.text_input("Custom nulls (comma)", value="") if drop_null else ""

            default_save = _next_key(source_key if source_key != "base_data" else "base_data")
            save_key = st.text_input("Save key", default_save)
            preview = st.button("Preview clean")
            save = st.button("Save clean")

            params = dict(
                drop_pe=drop_pe,
                pe_thresh=pe_thresh,
                fill_type=fill_type,
                select_cols=select_cols,
                keep_cols=keep_cols,
                filter_rows=filter_rows,
                filter_col=filter_col,
                filter_op=filter_op,
                filter_val=filter_val,
                drop_dup=drop_dup,
                drop_null=drop_null,
                null_types=null_types,
                custom_nulls=custom_nulls,
                type_map=tm,
            )

            if preview or save:
                cleaned = _clean_dataframe(df_src, params)
                st.dataframe(cleaned.head(10))
                if preview:
                    st.session_state["latest_clean_df"] = cleaned
                if save:
                    state.set(save_key, cleaned)
                    state.add_dynamic_data_key(save_key, "normal")
                    st.success(f"Saved `{save_key}`")
                    csv_bytes = cleaned.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="Download cleaned CSV",
                        data=csv_bytes,
                        file_name=f"{save_key}.csv",
                        mime="text/csv",
                    )

        # -------- SPMF Tab --------
        with tabs[2]:
            dyn = state.get_dynamic_data_keys()
            normal_keys = [e["key"] for e in dyn if e["category"] == "normal"]
            if source_key == "base_data":
                normal_keys.insert(0, "base_data")
            if not normal_keys:
                st.info("No cleaned data available.")
                return

            base_key = st.selectbox("Base data", normal_keys)
            df0 = base_df if base_key == "base_data" else state.get(base_key)
            tm = st.session_state["col_types"]
            dt_opts = [c for c, t in tm.items() if t == "Datetime"]
            dt_col = st.selectbox("Datetime column", dt_opts)
            fmt = st.text_input("Datetime format", "%m/%d/%Y %I:%M:%S %p")
            grp = st.text_input("Group by column", "zip_code")
            fields = st.multiselect("Fields", df0.columns.tolist())

            bins_conf = {}
            for c in fields:
                if tm.get(c) == "Numeric":
                    raw_bins = st.text_input(f"{c} bins", "0,1,2,10", key=f"{c}_bins")
                    raw_labels = st.text_input(f"{c} labels", "V0,V1,V2", key=f"{c}_labels")
                    try:
                        bins = [float(x) for x in raw_bins.split(",") if x.strip()]
                        labels = [x.strip() for x in raw_labels.split(",") if x.strip()]
                        if len(labels) == len(bins) - 1:
                            bins_conf[c] = {"bins": bins, "labels": labels}
                        else:
                            st.warning(f"{c}: labels count should be len(bins)-1")
                    except ValueError:
                        st.warning(f"{c}: invalid bins")

            spmf_key = st.text_input("SPMF save key", "spmf_v1")
            prev_spmf = st.button("Preview SPMF")
            save_spmf = st.button("Save SPMF")

            def _to_spmf():
                d1 = ops.parse_time_for_spmf(df0, dt_col, fmt)
                d1["groupid"] = d1[grp].astype(str) + "_" + d1["dategroup"]
                d2 = ops.discretize_fields(d1, bins_conf) if bins_conf else d1
                d2 = d2.dropna(subset=fields)
                dict_df, it2id = ops.build_spmf_dictionary(d2, fields)
                path = ops.write_spmf_file(d2, fields, it2id)
                sp_df = ops.spmf_to_dataframe(path)
                return dict_df, path, sp_df

            if prev_spmf or save_spmf:
                dict_df, path, sp_df = _to_spmf()
                st.dataframe(dict_df.head(10))
                st.dataframe(sp_df.head(10))
                if save_spmf:
                    state.set(f"{spmf_key}_dict", dict_df)
                    state.add_dynamic_data_key(f"{spmf_key}_dict", "spmf")
                    state.set(f"{spmf_key}_file", path)
                    state.add_dynamic_data_key(f"{spmf_key}_file", "spmf")
                    state.set(f"{spmf_key}_df", sp_df)
                    state.add_dynamic_data_key(f"{spmf_key}_df", "spmf")
                    st.success(f"SPMF saved as `{spmf_key}`")