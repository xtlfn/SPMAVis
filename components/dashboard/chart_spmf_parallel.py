# components/dashboard/chart_spmf_parallel.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import components.state_manager as state

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

    # 1) Expand and filter patterns: only keep patterns with ≥2 fields present
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
        # Count non-null fields
        if sum(1 for v in fv.values() if v is not None) < 2:
            continue
        fv["support"] = sup
        rows.append(fv)

    df = pd.DataFrame(rows)
    if df.empty:
        st.warning("No patterns with at least two fields present.")
        return

    # 2) Fill missing placeholders
    #df[fields] = df[fields].fillna(" ")

    # 3) Aggregate support for each unique combination
    agg = df.groupby(fields, dropna=False, as_index=False).agg({"support": "sum"})

    # 4) Prepare dimensions for go.Parcats
    dimensions = []
    for fld in fields:
        # ensure missing placeholder included in category order
        categories = list(agg[fld].unique())
        dimensions.append({
            "label": fld,
            "values": agg[fld].tolist(),
            "categoryorder": "array",
            "categoryarray": categories
        })

    # 5) Configure line coloring by aggregated support
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
    fig.update_layout(margin=dict(l=50, r=50, t=50, b=50))
    st.plotly_chart(fig, use_container_width=True)

def render_config_ui(patterns, window):
    if not isinstance(patterns, list) or not patterns:
        st.info("No patterns data for configuration.")
        return

    # Discover available fields from patterns
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

    selected = window.get("settings", {}).get("fields", options[:2])
    fields = st.multiselect(
        "Select fields to include",
        options,
        default=selected,
        key=f"{window['id']}_parallel_fields"
    )

    if st.button("Save Settings", key=f"save_parallel_{window['id']}"):
        if len(fields) < 2:
            st.error("Please select at least two fields.")
        else:
            window["settings"] = {"fields": fields}
            st.success("Settings saved.")