# components/dashboard/chart_spmf_heatmap.py

import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from itertools import combinations
from collections import defaultdict
import components.state_manager as state

DEFAULT_HEIGHT = 420

def render(data_key, settings=None):
    patterns = state.get(data_key)
    if not isinstance(patterns, list) or not patterns:
        st.warning("No pattern list found. Please select a `*_patterns` data source.")
        return

    cfg = settings or {}
    top_n = cfg.get("top_n", 10)
    height = cfg.get("height", DEFAULT_HEIGHT)

    field_support = defaultdict(int)
    for pat in patterns:
        sup = pat.get("support", 1) or 1
        fields = {item.split("=", 1)[0] for seq in pat["sequence"] for item in seq if "=" in item}
        for f in fields:
            field_support[f] += sup

    top_fields = [
        f
        for f, _ in sorted(field_support.items(), key=lambda x: x[1], reverse=True)[:top_n]
    ]
    if not top_fields:
        st.info("No fields to display.")
        return

    mat = pd.DataFrame(0.0, index=top_fields, columns=top_fields)
    for pat in patterns:
        sup = pat.get("support", 1) or 1
        fields = {item.split("=", 1)[0] for seq in pat["sequence"] for item in seq if "=" in item}
        sel = fields & set(top_fields)
        for a, b in combinations(sorted(sel), 2):
            mat.at[a, b] += sup
            mat.at[b, a] += sup

    mat_log = np.log10(mat + 1)
    fig = px.imshow(
        mat_log,
        x=top_fields,
        y=top_fields,
        labels={"x": "Field", "y": "Field", "color": "log10(Support+1)"},
        aspect="equal",
        color_continuous_scale="Blues",
        height=height
    )
    fig.update_layout(margin=dict(l=50, r=20, t=40, b=40))
    st.plotly_chart(fig, use_container_width=True)


def render_config_ui(df, window):
    data_key = window["data_key"]
    patterns = state.get(data_key) or []

    all_fields = {
        item.split("=", 1)[0]
        for pat in patterns
        for seq in pat["sequence"]
        for item in seq if "=" in item
    }
    num_fields = len(all_fields)

    cfg = window.get("settings", {}) or {}

    top_n = st.number_input(
        "Top N fields",
        min_value=1,
        max_value=num_fields,
        value=cfg.get("top_n", min(10, num_fields)),
        key=f"{window['id']}_heat_topn"
    )
    min_co = st.slider(
        "Min co-occurrence (log10)",
        0.0,
        float(np.log10(max(1, max(cfg.get("raw_counts", [1])) + 1))),
        value=cfg.get("min_log_co", 0.0),
        key=f"{window['id']}_heat_minco"
    )
    norm = st.selectbox(
        "Normalization",
        ["none", "row", "column", "total"],
        index=["none", "row", "column", "total"].index(cfg.get("norm", "none")),
        key=f"{window['id']}_heat_norm"
    )
    order = st.selectbox(
        "Field ordering",
        ["global_freq", "alphabetical", "original"],
        index=["global_freq", "alphabetical", "original"].index(cfg.get("order", "global_freq")),
        key=f"{window['id']}_heat_order"
    )
    triangle = st.checkbox(
        "Show only upper triangle",
        value=cfg.get("triangle", True),
        key=f"{window['id']}_heat_tri"
    )

    height = st.number_input(
        "Height (px)",
        min_value=200,
        max_value=1200,
        value=cfg.get("height", DEFAULT_HEIGHT),
        key=f"{window['id']}_heat_height"
    )

    if st.button("Save Heatmap Settings", key=f"save_{window['id']}"):
        window["settings"] = {
            "top_n": int(top_n),
            "min_log_co": float(min_co),
            "norm": norm,
            "order": order,
            "triangle": bool(triangle),
            "height": height
        }
        st.success("Settings saved.")