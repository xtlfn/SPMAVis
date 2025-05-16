# components/dashboard/chart_spmf.py

import streamlit as st
import components.state_manager as state


def render(data_key=None, settings=None):
    """
    Display top-K sequential patterns as horizontal pill-style flows with individual attribute pills and support values.
    """
    patterns = state.get(data_key)
    if not isinstance(patterns, list) or not patterns:
        st.warning("No pattern list found. Please select a `*_patterns` data source.")
        return

    # Determine Top K
    top_k = 10
    if isinstance(settings, dict):
        try:
            top_k = int(settings.get("top_k", top_k))
        except:
            pass

    # Sort patterns by descending support and select top_k
    sorted_patterns = sorted(
        patterns,
        key=lambda p: p.get("support", 0),
        reverse=True
    )[:top_k]

    # Render each pattern as a flow of attribute pills
    for idx, pat in enumerate(sorted_patterns, start=1):
        support = pat.get("support", 0)
        seq = pat.get("sequence", [])
        # Flatten all attribute items into a single list
        flat_items = [item for itemset in seq for item in itemset]
        # Build pill HTML for each attribute
        pill_list = []
        for itm in flat_items:
            pill_list.append(
                f"<span style='display:inline-block; background-color:#e0f3ff;"
                "border:1px solid #90caff; border-radius:10px; padding:4px 8px;"
                f"margin-right:4px'>{itm}</span>"
            )
        # Join pills with arrow separators
        separator = "<span style='font-size:16px; margin:0 4px;'>&#8594;</span>"
        flow_html = separator.join(pill_list)
        # Compose final HTML line with support annotation
        line_html = (
            f"<div style='margin-bottom:12px;'>"
            f"<strong>{idx}.</strong>&nbsp;{flow_html}&nbsp;"
            f"<em style='color:#666;'>(support: {support})</em>"
            f"</div>"
        )
        st.markdown(line_html, unsafe_allow_html=True)


def render_config_ui(patterns, window):
    """
    Configuration for pattern list: select number of Top K patterns to display.
    """
    cfg = window.get("settings", {}) or {}
    current = cfg.get("top_k", 10)
    top_k = st.number_input(
        "Top K patterns to display", min_value=1, max_value=200,
        value=int(current), key=f"{window['id']}_topk"
    )
    if st.button("Save Pattern List Settings", key=f"save_spmf_{window['id']}"):
        window["settings"] = {"top_k": top_k}
        st.success("Settings saved.")
