# components/sidebar/algorithm.py

import streamlit as st
import components.state_manager as state
import components.spmf.algorithm_registry as registry
import components.spmf.spmf_executor as executor
from components.spmf.spmf_parser import parse_spmf_output, parse_to_dataframe

def render_algorithm_panel():
    state.init_state()
    with st.expander("📌 Algorithm Runner", expanded=False):
        st.header("Sequential Pattern Mining")

        dynamic = state.get_dynamic_data_keys()
        spmf_file_keys = [
            e["key"]
            for e in dynamic
            if e["category"] == "spmf" and e["key"].endswith("_file")
        ]
        if not spmf_file_keys:
            st.warning("Please save at least one SPMF file version (ending with '_file') in Data Tool first.")
            return

        spmf_input_key = st.selectbox("Select SPMF file version (_file)", spmf_file_keys)
        input_file = state.get(spmf_input_key)
        if not isinstance(input_file, str):
            st.error(f"Selected version `{spmf_input_key}` is not a file path.")
            return

        algo_list = registry.get_available_algorithms()
        selected_algo = st.selectbox("Select Algorithm", algo_list)
        if not selected_algo:
            st.warning("Please select an algorithm.")
            return

        params = {}
        for p in registry.get_algorithm_parameters(selected_algo):
            if p == "min_support":
                params[p] = st.slider("Min Support", 0.0, 1.0, 0.5, 0.01)
            elif p == "max_support":
                params[p] = st.slider("Max Support", 0.0, 1.0, 1.0, 0.01)
            elif p == "max_pattern_length":
                params[p] = st.number_input("Max Pattern Length", 1, 100, 100)
            elif p == "top_k":
                params[p] = st.number_input("Top-K", 1, 100, 10)

        if st.button("Run Algorithm"):
            with st.spinner("Running Algorithm..."):
                try:
                    result_df = executor.run_spmf(selected_algo, input_file, params)

                    output_key = f"{spmf_input_key}_output"
                    state.set(output_key, result_df)
                    state.add_dynamic_data_key(output_key, "spmf")

                    dict_key = spmf_input_key.replace("_file", "_dict")
                    dict_df = state.get(dict_key)
                    if dict_df is None:
                        st.error(f"Dictionary not found for `{spmf_input_key}` (expected `{dict_key}`).")
                        return

                    patterns = parse_spmf_output(result_df, dict_df)

                    patterns_key = spmf_input_key.replace("_file", "_patterns")
                    state.set(patterns_key, patterns)
                    state.add_dynamic_data_key(patterns_key, "spmf")


                    summary_df = parse_to_dataframe(patterns)
                    summary_key = spmf_input_key.replace("_file", "_summary")
                    state.set(summary_key, summary_df)
                    state.add_dynamic_data_key(summary_key, "normal")

                    st.success("Algorithm run completed successfully! Results have been saved.")
                except Exception as e:
                    st.error(f"Error running algorithm: {e}")
