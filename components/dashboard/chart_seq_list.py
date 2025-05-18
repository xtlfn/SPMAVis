# components/dashboard/chart_spmf.py

import streamlit as st
import components.state_manager as state

DEFAULT_HEIGHT = 420

def render(data_key=None, settings=None):
    patterns = state.get(data_key)
    if not isinstance(patterns, list) or not patterns:
        st.warning("No pattern list found. Please select a `*_patterns` data source.")
        return

    cfg = settings or {}
    try:
        top_k = int(cfg.get("top_k", 10))
    except:
        top_k = 10
    height = cfg.get("height", DEFAULT_HEIGHT)

    sorted_patterns = sorted(
        patterns,
        key=lambda p: p.get("support", 0),
        reverse=True
    )[:top_k]

    lines = []
    for idx, pat in enumerate(sorted_patterns, start=1):
        support = pat.get("support", 0)
        seq = pat.get("sequence", [])
        flat_items = [item for itemset in seq for item in itemset]
        pill_list = []
        for itm in flat_items:
            pill_list.append(
                f"<span style='display:inline-block; "
                "background-color:#e0f3ff; border:1px solid #90caff; "
                "border-radius:10px; padding:4px 8px; margin-right:4px;'>"
                f"{itm}</span>"
            )
        separator = "<span style='font-size:16px; margin:0 4px;'>&#8594;</span>"
        flow_html = separator.join(pill_list)
        line_html = (
            f"<div style='margin-bottom:12px;'>"
            f"<strong>{idx}.</strong>&nbsp;{flow_html}&nbsp;"
            f"<em style='color:#666;'>(support: {support})</em>"
            f"</div>"
        )
        lines.append(line_html)

    container_html = (
        f"<div style='height:{height}px; overflow:auto; padding-right:10px;'>"
        + "".join(lines) +
        "</div>"
    )
    st.markdown(container_html, unsafe_allow_html=True)


def render_config_ui(patterns, window):
    cfg = window.get("settings", {}) or {}
    current_k = cfg.get("top_k", 10)

    top_k = st.number_input(
        "Top K patterns to display",
        min_value=1,
        max_value=200,
        value=int(current_k),
        key=f"{window['id']}_topk"
    )

    height = st.number_input(
        "Height (px)",
        min_value=200,
        max_value=1200,
        value=cfg.get("height", DEFAULT_HEIGHT),
        key=f"{window['id']}_height"
    )

    if st.button("Save Pattern List Settings", key=f"save_spmf_{window['id']}"):
        window["settings"] = {
            "top_k": int(top_k),
            "height": height
        }
        st.success("Settings saved.")
