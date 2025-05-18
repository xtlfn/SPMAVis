# components/dashboard/chart_map.py

import streamlit as st
import plotly.express as px
import pandas as pd
import components.state_manager as state

DEFAULT_HEIGHT = 420

def render(data_key, settings=None):
    df = state.get(data_key)
    if df is None or not isinstance(df, pd.DataFrame):
        st.warning("No data available.")
        return

    settings = settings or {}
    lat = settings.get("lat")
    lon = settings.get("lon")
    color = settings.get("color")
    height = settings.get("height", DEFAULT_HEIGHT)

    if not lat or not lon or lat not in df.columns or lon not in df.columns:
        st.warning("Please configure latitude and longitude fields.")
        return

    fig = px.scatter_mapbox(
        df,
        lat=lat,
        lon=lon,
        color=color if color in df.columns else None,
        zoom=6,
        center={"lat": 35.8, "lon": -86.5},
        height=height,
        mapbox_style="carto-positron",
    )

    st.plotly_chart(fig, use_container_width=True, config={
        "scrollZoom": True,
        "displayModeBar": True,
        "modeBarButtonsToRemove": []
    })

def render_config_ui(df, window):
    st.markdown("#### Configure Map Chart")

    lat_field = st.selectbox("Latitude Field", df.columns, key=f"{window['id']}_lat")
    lon_field = st.selectbox("Longitude Field", df.columns, key=f"{window['id']}_lon")
    color_field = st.selectbox("Color Field (optional)", [None] + list(df.columns), key=f"{window['id']}_color")

    height = st.number_input(
        "Height (px)",
        min_value=200,
        max_value=1200,
        value=window.get("settings", {}).get("height", DEFAULT_HEIGHT),
        key=f"{window['id']}_height"
    )

    settings = {
        "mode": "scatter",
        "lat": lat_field,
        "lon": lon_field,
        "color": color_field,
        "height": height
    }

    if st.button("Save Chart Settings", key=f"save_{window['id']}"):
        window["settings"] = settings
        st.success("Map settings saved.")