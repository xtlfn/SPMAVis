import streamlit as st
import plotly.express as px
import pandas as pd
import components.state_manager as state

def render(data_key=None, settings=None):
    df = state.get(data_key)
    if not isinstance(df, pd.DataFrame) or df.empty:
        st.warning("Please select *_summary data source first.")
        return

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
        height=600,
    )
    st.plotly_chart(fig, use_container_width=True)

def render_config_ui(df, window):
    st.info("no config options available for this chart.")