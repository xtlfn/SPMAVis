# components/dashboard/chart_spmf_heatmap.py

import streamlit as st
import plotly.express as px
import pandas as pd
import components.state_manager as state
from collections import defaultdict

def render(data_key=None, settings=None):
    st.subheader("Field vs. Value Heatmap")

    patterns = state.get(data_key)
    if not isinstance(patterns, list) or not patterns:
        st.warning("No pattern list found. Please select a `*_patterns` data source.")
        return

    # Aggregate support for each field=value pair
    counter = defaultdict(int)
    for pattern in patterns:
        support = pattern.get("support", 1) or 1
        for itemset in pattern.get("sequence", []):
            for item in itemset:
                if "=" in item:
                    field, val = item.split("=", 1)
                    counter[(field.strip(), val.strip())] += support

    if not counter:
        st.info("No data to visualize.")
        return

    # Build DataFrame and pivot
    data = [{"field": f, "value": v, "support": c} for (f, v), c in counter.items()]
    df = pd.DataFrame(data)
    pivot = df.pivot(index="value", columns="field", values="support").fillna(0)

    fig = px.imshow(
        pivot,
        labels=dict(x="Field", y="Value", color="Support"),
        color_continuous_scale="Blues",
        aspect="auto"
    )
    fig.update_layout(margin=dict(t=40, b=40, l=80, r=40))

    st.plotly_chart(fig, use_container_width=True)

def render_config_ui(df, window):
    st.info("No configurable options for Heatmap.")
