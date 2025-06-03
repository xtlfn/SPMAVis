import os
import json
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import components.state_manager as state

DEFAULT_HEIGHT = 420
GEOJSON_PATH = os.path.join(os.path.dirname(__file__), "nsw.geojson")
GEO_PROP = "nsw_loca_2"

def render(data_key, settings=None):
    df = state.get(data_key)
    if df is None or not isinstance(df, pd.DataFrame):
        st.warning("No data available.")
        return

    settings = settings or {}
    mode = settings.get("mode", "Scatter")

    if mode == "Scatter":
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
            center={"lat": -33.87, "lon": 151.2},
            height=height,
            mapbox_style="carto-positron"
        )
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})
        return

    if mode == "Cluster":
        lat = settings.get("lat")
        lon = settings.get("lon")
        height = settings.get("height", DEFAULT_HEIGHT)

        if not lat or not lon or lat not in df.columns or lon not in df.columns:
            st.warning("Please configure latitude and longitude fields.")
            return

        fig = go.Figure(go.Scattermapbox(
            lat=df[lat],
            lon=df[lon],
            mode='markers',
            marker=dict(size=6, color='blue'),
            cluster=dict(enabled=True, maxzoom=12, step=50)
        ))
        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=6,
            mapbox_center={"lat": -33.87, "lon": 151.2},
            height=height,
            margin={"r":0, "t":0, "l":0, "b":0}
        )
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})
        return

    if mode == "Choropleth":
        region_field = settings.get("region_field")
        height = settings.get("height", DEFAULT_HEIGHT)

        if not region_field or region_field not in df.columns:
            st.warning("Please configure region field for choropleth.")
            return

        counts = (
            df[region_field]
            .str.upper().str.strip()
            .value_counts()
            .reset_index(name="accident_count")
        )
        counts.columns = [GEO_PROP, "accident_count"]

        gdf = gpd.read_file(GEOJSON_PATH)
        gdf[GEO_PROP] = gdf[GEO_PROP].str.upper().str.strip()

        merged = gdf.merge(counts, on=GEO_PROP, how="left")
        merged["accident_count"] = merged["accident_count"].fillna(0)

        with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)

        fig = px.choropleth_mapbox(
            merged,
            geojson=geojson_data,
            locations=GEO_PROP,
            featureidkey=f"properties.{GEO_PROP}",
            color="accident_count",
            color_continuous_scale="OrRd",
            mapbox_style="carto-positron",
            zoom=5.3,
            center={"lat": -33.87, "lon": 151.2},
            opacity=0.6,
            hover_name=GEO_PROP,
            height=height
        )
        fig.update_layout(margin={"r":0, "t":30, "l":0, "b":0})
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})
        return

    st.warning("Unknown map mode.")

def render_config_ui(df, window):
    st.markdown("#### Configure Map Chart")

    current_mode = window.get("settings", {}).get("mode", "Scatter")
    mode = st.selectbox(
        "Map Type",
        ["Scatter", "Cluster", "Choropleth"],
        index={"Scatter":0, "Cluster":1, "Choropleth":2}.get(current_mode, 0),
        key=f"{window['id']}_mode"
    )
    settings = {"mode": mode}

    if mode in ["Scatter", "Cluster"]:
        lat_field = st.selectbox("Latitude Field", df.columns, key=f"{window['id']}_lat")
        lon_field = st.selectbox("Longitude Field", df.columns, key=f"{window['id']}_lon")
        color_field = st.selectbox(
            "Color Field (optional)",
            [None] + list(df.columns),
            key=f"{window['id']}_color"
        )
        height = st.number_input(
            "Height (px)",
            min_value=200, max_value=1200,
            value=window.get("settings", {}).get("height", DEFAULT_HEIGHT),
            key=f"{window['id']}_height"
        )
        settings.update({"lat": lat_field, "lon": lon_field, "color": color_field, "height": height})

    else:
        region_field = st.selectbox(
            "Region Field", df.columns,
            index=list(df.columns).index("Town") if "Town" in df.columns else 0,
            key=f"{window['id']}_region"
        )
        height = st.number_input(
            "Height (px)",
            min_value=200, max_value=1200,
            value=window.get("settings", {}).get("height", DEFAULT_HEIGHT),
            key=f"{window['id']}_height"
        )
        settings.update({"region_field": region_field, "height": height})

    if st.button("Save Chart Settings", key=f"save_{window['id']}"):
        window["settings"] = settings
        st.success("Map settings saved.")
