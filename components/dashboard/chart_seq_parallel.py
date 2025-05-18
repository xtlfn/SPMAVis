# components/dashboard/chart_spmf_parallel.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import components.state_manager as state

DEFAULT_HEIGHT = 420

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

    height = cfg.get("height", DEFAULT_HEIGHT)

    # prepare data rows
    rows = []
    for pat in patterns:
        sup = pat.get("support", 0)
        fv = {fld: None for fld in fields}
        for seq in pat.get("sequence", []):
            for item in seq:
                if "=" in item:
                    f, v = item.split("=", 1)
                    if f in fv:
                        fv[f] = v
        if sum(1 for v in fv.values() if v is not None) < 2:
            continue
        fv["support"] = sup
        rows.append(fv)

    df = pd.DataFrame(rows)
    if df.empty:
        st.warning("No patterns with at least two fields present.")
        return

    agg = df.groupby(fields, dropna=False, as_index=False).agg({"support": "sum"})

    dimensions = []
    for fld in fields:
        categories = list(agg[fld].unique())
        dimensions.append({
            "label": fld,
            "values": agg[fld].tolist(),
            "categoryorder": "array",
            "categoryarray": categories
        })

    line = {
        "color": agg["support"].tolist(),
        "colorscale": "Blues",
        "shape": "hspline"
    }

    fig = go.Figure(go.Parcats(
        dimensions=dimensions,
        line=line,
        hoveron="color",
        hoverinfo="all"
    ))
    fig.update_layout(
        margin=dict(l=50, r=50, t=50, b=50),
        height=height
    )
    st.plotly_chart(fig, use_container_width=True)


def render_config_ui(patterns, window):
    if not isinstance(patterns, list) or not patterns:
        st.info("No patterns data for configuration.")
        return

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
        "Select fields to include",
        options,
        default=selected,
        key=f"{window['id']}_parallel_fields"
    )

    height = st.number_input(
        "Height (px)",
        min_value=200,
        max_value=1200,
        value=cfg.get("height", DEFAULT_HEIGHT),
        key=f"{window['id']}_parallel_height"
    )

    if st.button("Save Settings", key=f"save_parallel_{window['id']}"):
        if len(fields) < 2:
            st.error("Please select at least two fields.")
        else:
            new_cfg = cfg.copy()
            new_cfg["fields"] = fields
            new_cfg["height"] = height
            window["settings"] = new_cfg
            st.success("Settings saved.")
