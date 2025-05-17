# components/sidebar/algorithm.py

import streamlit as st
import components.state_manager as state
import components.spmf.algorithm_registry as registry
import components.spmf.spmf_executor as executor
from components.spmf.spmf_parser import (
    parse_spmf_output,
    parse_to_dataframe,
)


def _spmf_files() -> list[str]:
    dyn = state.get_dynamic_data_keys()
    return [
        e["key"]
        for e in dyn
        if e["category"] == "spmf" and e["key"].endswith("_file")
    ]


def _ui_param_input(param_name: str):
    if param_name == "min_support":
        return st.slider("min_support", 0.0, 1.0, 0.5, 0.01)
    if param_name == "max_support":
        return st.slider("max_support", 0.0, 1.0, 1.0, 0.01)
    if param_name == "max_pattern_length":
        return st.number_input("max_pattern_length", 1, 1000, 100)
    if param_name in {"top_k", "k"}:
        return st.number_input(param_name, 1, 1000, 10)
    if param_name == "min_conf":
        return st.slider("min_conf", 0.0, 1.0, 0.8, 0.01)
    if param_name == "allowed_items":
        st.caption("allowed_items – IDs of items allowed as rule consequent")
        dict_df = state.get(
            st.session_state["algo_selected_file"].replace("_file", "_dict")
        )
        if dict_df is not None:
            picked = st.multiselect(
                "allowed_items",
                dict_df["ID"].tolist(),
            )
            return ",".join(map(str, picked))
        return st.text_input("allowed_items", "")
    return st.text_input(param_name)


def render_algorithm_panel():
    state.init_state()
    with st.expander("📌 Algorithm Runner", expanded=False):
        st.header("SPMF Algorithm Runner")

        file_keys = _spmf_files()
        if not file_keys:
            st.info("No *_file artefacts saved yet. Use Data Tool first.")
            return

        file_key = st.selectbox(
            "Input SPMF file",
            file_keys,
            key="algo_selected_file",
        )
        in_path = state.get(file_key)

        # choose pattern category first
        mode = st.radio(
            "Pattern category",
            ["Sequence", "Association"],
            horizontal=True,
            key="algo_category",
        )
        algo_cat = "seq" if mode == "Sequence" else "rule"

        algo_options = [
            a
            for a in registry.get_available_algorithms()
            if registry.get_algorithm_cat(a) == algo_cat
        ]
        algo_name = st.selectbox("Algorithm", algo_options)
        if not algo_name:
            return

        params = {
            p: _ui_param_input(p)
            for p in registry.get_algorithm_parameters(algo_name)
        }

        if st.button("Run"):
            with st.spinner("Running..."):
                try:
                    df_raw = executor.run_spmf(algo_name, in_path, params)

                    out_key = f"{file_key}_output"
                    state.set(out_key, df_raw)
                    state.add_dynamic_data_key(out_key, "spmf")

                    dict_df = state.get(file_key.replace("_file", "_dict"))

                    if algo_cat == "seq":
                        patterns = parse_spmf_output(df_raw, dict_df)
                        summary = parse_to_dataframe(patterns)

                        patterns_key = file_key.replace("_file", "_patterns")
                        state.set(patterns_key, patterns)
                        state.add_dynamic_data_key(patterns_key, "spmf")
                    else:  # rule category
                        summary = df_raw

                    summary_key = file_key.replace("_file", "_summary")
                    state.set(summary_key, summary)
                    state.add_dynamic_data_key(summary_key, "normal")

                    st.success("Algorithm completed - results saved.")
                except Exception as err:
                    st.error(f"SPMF execution failed: {err}")