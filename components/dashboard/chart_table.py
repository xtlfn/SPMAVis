# components/dashboard/chart_table.py

import streamlit as st
import components.state_manager as state

DEFAULT_HEIGHT = 420

def render(data_key=None, settings=None):
    if not data_key:
        st.info("No data source selected for this chart.")
        return

    data = state.get(data_key)

    if data is not None:
        height = settings.get("height", DEFAULT_HEIGHT) if settings else DEFAULT_HEIGHT
        st.dataframe(data, height=height)
    else:
        st.warning(f"No data found for key: `{data_key}`.")

def render_config_ui(df, window):
    st.markdown("#### Configure Table Chart")

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