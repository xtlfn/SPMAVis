# components/dashboard/chart_rule_heatmap.py

import streamlit as st
import plotly.express as px
import pandas as pd
import components.state_manager as state

DEFAULT_HEIGHT = 420

def render(data_key=None, settings=None):
    df = state.get(data_key)
    if df is None or df.empty:
        st.warning("No rule data available.")
        return

    settings = settings or {}
    height   = settings.get("height", DEFAULT_HEIGHT)
    attr1    = settings.get("attr1")
    attr2    = settings.get("attr2")

    rule_maps = (
        df["Antecedent"]
        .str.split(" & ")
        .apply(lambda lst: dict(item.split("=",1) for item in lst))
    )
    rules_df = pd.DataFrame(rule_maps.tolist())

    if not attr1 or not attr2:
        st.info("Please select two attributes in the chart settings to see their co-occurrence heatmap.")
        return

    mat = pd.crosstab(rules_df[attr1], rules_df[attr2])

    fig = px.imshow(
        mat,
        labels={"x": attr2, "y": attr1, "color": "Count"},
        text_auto=True,
        color_continuous_scale="Blues",
        aspect="auto",
        height=height,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_config_ui(df, window):
    st.markdown("#### Configure Rule Heatmap Chart")
    settings = window.get("settings", {}) or {}

    sample = df["Antecedent"].iloc[0].split(" & ")
    attrs  = [item.split("=",1)[0] for item in sample]

    attr1 = st.selectbox(
        "Row attribute",
        options=attrs,
        index=attrs.index(settings.get("attr1")) if settings.get("attr1") in attrs else 0,
        key=f"{window['id']}_attr1"
    )
    attr2 = st.selectbox(
        "Column attribute",
        options=[a for a in attrs if a != attr1],
        index=0,
        key=f"{window['id']}_attr2"
    )

    height = st.number_input(
        "Height (px)",
        min_value=200, max_value=1200,
        value=settings.get("height", DEFAULT_HEIGHT),
        key=f"{window['id']}_height"
    )

    if st.button("Save Chart Settings", key=f"save_{window['id']}"):
        settings["attr1"] = attr1
        settings["attr2"] = attr2
        settings["height"] = height
        window["settings"] = settings
        st.success("Settings saved.")