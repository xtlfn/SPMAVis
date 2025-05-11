# components/dashboard/chart_spmf.py

import streamlit as st
import pandas as pd
import components.state_manager as state
from components.spmf.spmf_parser import parse_spmf_output

def render(data_key=None, settings=None):
    if not data_key:
        st.warning("No data key provided.")
        return

    result_df = state.get(data_key)
    dict_df = state.get("spmf_dictionary")

    if result_df is None or dict_df is None:
        st.warning("SPMF output or dictionary not found.")
        return

    settings = settings or {}
    top_k = settings.get("top_k", 10)
    sort_by = settings.get("sort_by", "support")
    display = settings.get("display", "text")

    patterns = parse_spmf_output(result_df, dict_df)

    if sort_by == "support":
        patterns.sort(key=lambda x: x.get("support", 0), reverse=True)

    st.markdown(f"### Top {top_k} Frequent Patterns")

    for p in patterns[:top_k]:
        support = p.get("support", "?")
        seq = p["sequence"]
        text = " → ".join([" + ".join(itemset) for itemset in seq])
        st.markdown(f"- **Pattern #{p['id']}** (Support: {support})\n\n{text}")

def render_config_ui(df, window):
    st.markdown("#### Configure Pattern Viewer")

    settings = window.get("settings", {})

    top_k = st.number_input("Top K Patterns", min_value=1, max_value=100, value=settings.get("top_k", 10), key=f"{window['id']}_topk")
    sort_by = st.selectbox("Sort By", ["support", "length"], index=0, key=f"{window['id']}_sort")
    display = st.selectbox("Display Format", ["text"], index=0, key=f"{window['id']}_display")

    settings.update({
        "top_k": top_k,
        "sort_by": sort_by,
        "display": display
    })

    if st.button("Save Chart Settings", key=f"save_{window['id']}"):
        window["settings"] = settings
        st.success("Pattern viewer settings saved.")