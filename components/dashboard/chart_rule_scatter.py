# components/dashboard/chart_rule_scatter.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import components.state_manager as state
import pandas as pd

DEFAULT_HEIGHT = 420
DEFAULT_TOP_N = 5

def render(data_key=None, settings=None):
    df = state.get(data_key)
    if not isinstance(df, pd.DataFrame) or df.empty:
        st.warning("No rule data available.")
        return

    cfg = settings or {}
    df = df[df["Support"] >= cfg.get("min_support", 0)]
    df = df[df["Confidence"] >= cfg.get("min_confidence", 0.0)]

    has_lift = "Lift" in df.columns
    if has_lift:
        df = df[df["Lift"] >= cfg.get("min_lift", df["Lift"].min())]

    if df.empty:
        st.info("No rules match the current filters.")
        return

    size_metric = "Lift" if has_lift else None
    color_metric = "Lift" if has_lift else None

    height = cfg.get("height", DEFAULT_HEIGHT)
    fig = px.scatter(
        df,
        x="Support",
        y="Confidence",
        size=size_metric,
        color=color_metric,
        hover_data=["Rule ID", "Antecedent", "Consequent"] + (["Lift"] if has_lift else []),
        height=height,
        labels={"Support": "Support", "Confidence": "Confidence"}
    )

    top_n = cfg.get("top_n", DEFAULT_TOP_N)
    if has_lift:
        top = df.nlargest(top_n, "Lift")
    else:
        top = df.nlargest(top_n, "Support")

    fig.add_trace(go.Scatter(
        x=top["Support"],
        y=top["Confidence"],
        mode="text",
        text=top["Rule ID"],
        textposition="top right",
        showlegend=False
    ))

    st.plotly_chart(fig, use_container_width=True)


def render_config_ui(df, window):
    st.markdown("#### Configure Support-Confidence Scatter")

    settings = window.get("settings", {}) or {}

    min_sup = st.number_input(
        "Min Support",
        min_value=0,
        value=settings.get("min_support", 0),
        step=1,
        key=f"{window['id']}_min_sup"
    )
    min_conf = st.slider(
        "Min Confidence",
        0.0, 1.0,
        value=settings.get("min_confidence", 0.0),
        key=f"{window['id']}_min_conf"
    )

    if "Lift" in df.columns:
        lift_min, lift_max = float(df["Lift"].min()), float(df["Lift"].max())
        min_lift = st.slider(
            "Min Lift",
            lift_min, lift_max,
            value=settings.get("min_lift", lift_min),
            key=f"{window['id']}_min_lift"
        )
    else:
        min_lift = None

    top_n = st.number_input(
        "Top N Labels",
        min_value=1,
        max_value=100,
        value=settings.get("top_n", DEFAULT_TOP_N),
        key=f"{window['id']}_top_n"
    )

    height = st.number_input(
        "Height (px)",
        min_value=200,
        max_value=1200,
        value=settings.get("height", DEFAULT_HEIGHT),
        key=f"{window['id']}_height"
    )

    if st.button("Save Chart Settings", key=f"save_{window['id']}"):
        new_cfg = {
            "min_support": int(min_sup),
            "min_confidence": float(min_conf),
            "top_n": int(top_n),
            "height": int(height)
        }
        if min_lift is not None:
            new_cfg["min_lift"] = float(min_lift)
        window["settings"] = new_cfg
        st.success("Settings saved.")