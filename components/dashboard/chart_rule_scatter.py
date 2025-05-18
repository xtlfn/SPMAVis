# components/dashboard/chart_rule_scatter.py

import streamlit as st
import plotly.express as px
import pandas as pd
import components.state_manager as state

DEFAULT_HEIGHT = 420

def render(data_key=None, settings=None):
    df = state.get(data_key)
    if not isinstance(df, pd.DataFrame) or df.empty:
        st.warning("Please select *_summary data source first.")
        return

    settings = settings or {}
    height = settings.get("height", DEFAULT_HEIGHT)

    y_metric = "Confidence"
    x_metric = "Support"
    size_metric = "Lift" if "Lift" in df.columns else None

    fig = px.scatter(
        df,
        x=x_metric,
        y=y_metric,
        size=size_metric,
        hover_data=["Antecedent", "Consequent"],
        title="Support-Confidence",
        height=height,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_config_ui(df, window):
    st.markdown("#### Configure Support-Confidence Scatter")

    height = st.number_input(
        "Height (px)",
        min_value=200,
        max_value=1200,
        value=window.get("settings", {}).get("height", DEFAULT_HEIGHT),
        key=f"{window['id']}_height"
    )

    if st.button("Save Chart Settings", key=f"save_{window['id']}"):
        settings = window.get("settings", {}) or {}
        settings["height"] = height
        window["settings"] = settings
        st.success("Settings saved.")