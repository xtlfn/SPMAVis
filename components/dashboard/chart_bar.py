# components/dashboard/chart_bar.py

import streamlit as st
import components.state_manager as state
import plotly.express as px
import pandas as pd

DEFAULT_HEIGHT = 420

def render(data_key, settings=None):
    df = state.get(data_key)
    if df is None or not isinstance(df, pd.DataFrame):
        st.warning("No data available.")
        return

    settings = settings or {}
    x = settings.get("x")
    y = settings.get("y")
    color = settings.get("color")
    aggfunc = settings.get("aggfunc", "count").lower()
    height = settings.get("height", DEFAULT_HEIGHT)

    if not x or x not in df.columns:
        st.warning("Invalid X axis.")
        return

    if y == "count":
        grouped = df.groupby(x).size().reset_index(name="count")
        fig = px.bar(
            grouped,
            x=x,
            y="count",
            color=color if color in grouped.columns else None,
            height=height
        )

    elif aggfunc == "none":
        if not y or y not in df.columns:
            st.warning("Invalid Y axis.")
            return
        fig = px.bar(
            df,
            x=x,
            y=y,
            color=color if color in df.columns else None,
            height=height
        )

    else:
        if not y or y not in df.columns:
            st.warning("Invalid Y axis.")
            return
        if not pd.api.types.is_numeric_dtype(df[y]):
            st.warning(f"Y axis field '{y}' is not numeric.")
            return
        grouped = df.groupby(x)[y].agg(aggfunc).reset_index()
        fig = px.bar(
            grouped,
            x=x,
            y=y,
            color=color if color in grouped.columns else None,
            height=height
        )

    st.plotly_chart(fig, use_container_width=True)


def render_config_ui(df, window):
    st.markdown("#### Configure Bar Chart")

    x = st.selectbox("X Axis", df.columns, key=f"{window['id']}_x")
    all_y_options = ["count"] + [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    y = st.selectbox("Y Axis", all_y_options, key=f"{window['id']}_y")

    disable_agg = (y == "count")
    if disable_agg:
        aggfunc = "count"
        st.text("Aggregation: count (auto applied)")
    else:
        aggfunc = st.selectbox(
            "Aggregation Function",
            ["None", "sum", "mean", "min", "max"],
            index=0,
            key=f"{window['id']}_agg"
        ).lower()

    color = st.selectbox("Color (optional)", [None] + list(df.columns), key=f"{window['id']}_color")

    height = st.number_input(
        "Height (px)",
        min_value=200,
        max_value=1200,
        value=window.get("settings", {}).get("height", DEFAULT_HEIGHT),
        key=f"{window['id']}_height"
    )

    if st.button("Save Chart Settings", key=f"save_{window['id']}"):
        window["settings"] = {
            "x": x,
            "y": y,
            "aggfunc": aggfunc,
            "color": color,
            "height": height
        }
        st.success("Settings saved.")