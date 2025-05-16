# components/dashboard/chart_spmf_sankey.py

import streamlit as st
import plotly.graph_objects as go
import components.state_manager as state
from collections import Counter


def render(data_key=None, settings=None):
    patterns = state.get(data_key)
    if not isinstance(patterns, list) or not patterns:
        st.warning("No pattern list found. Please select a `*_patterns` data source.")
        return

    cfg = settings or {}
    fields = cfg.get("fields", [])
    if len(fields) < 2:
        st.warning("Please select at least two fields in chart configuration.")
        return

    # Aggregate flows between adjacent fields
    flows = Counter()
    for pat in patterns:
        sup = pat.get("support", 0)
        # track last seen value for each field
        fv = {fld: None for fld in fields}
        for seq in pat.get("sequence", []):
            for item in seq:
                if "=" in item:
                    f, v = item.split("=", 1)
                    if f in fv:
                        fv[f] = v
        # sum support for each adjacent pair
        for i in range(len(fields) - 1):
            a = fv[fields[i]]
            b = fv[fields[i+1]]
            if a is not None and b is not None:
                src = f"{fields[i]}={a}"
                tgt = f"{fields[i+1]}={b}"
                flows[(src, tgt)] += sup

    if not flows:
        st.info("No co-occurrence flows to display for selected fields.")
        return

    # Build node-index mapping
    nodes = sorted({node for pair in flows for node in pair})
    index = {node: idx for idx, node in enumerate(nodes)}

    # Build source/target/value lists
    source, target, value = [], [], []
    for (src, tgt), w in flows.items():
        source.append(index[src])
        target.append(index[tgt])
        value.append(w)

    # Construct Sankey figure
    sankey = go.Sankey(
        node=dict(label=nodes, pad=15, thickness=20,
                  line=dict(color="black", width=0.5)),
        link=dict(source=source, target=target, value=value)
    )
    fig = go.Figure(sankey)
    fig.update_layout(
        title_text="Sequential Pattern Co-occurrence Sankey (sum of support)",
        font_size=12,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    st.plotly_chart(fig, use_container_width=True)


def render_config_ui(patterns, window):
    if not isinstance(patterns, list) or not patterns:
        st.info("No patterns data for configuration.")
        return

    # Discover available fields
    seen = set()
    options = []
    for pat in patterns:
        for seq in pat.get("sequence", []):
            for item in seq:
                if "=" in item:
                    f, _ = item.split("=", 1)
                    if f not in seen:
                        seen.add(f)
                        options.append(f)
    options.sort()

    cfg = window.get("settings", {}) or {}
    selected = cfg.get("fields", options[:2])

    fields = st.multiselect(
        "Select fields (in order) for Sankey",
        options,
        default=selected,
        key=f"{window['id']}_sankey_fields"
    )

    if st.button("Save Sankey Settings", key=f"save_sankey_{window['id']}"):
        if len(fields) < 2:
            st.error("Please select at least two fields.")
        else:
            window["settings"] = {"fields": fields}
            st.success("Settings saved.")
