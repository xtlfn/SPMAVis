# components/sidebar/chart_manager.py

import streamlit as st
import pandas as pd
import components.state_manager as state
import components.dashboard.chart_registry as chart_registry

WIDTH_OPTIONS = {
    "Small (25%)": 3,
    "Medium (50%)": 6,
    "Large (75%)": 9,
    "Full (100%)": 12,
}

def render_window_manager():
    state.init_state()

    with st.expander("📁 Chart Manager", expanded=False):

        mode = st.selectbox("Mode", ["Add New Window", "Existing Windows", "Configure Chart"])

        if mode == "Add New Window":
            st.subheader("Add New Window")

            available_charts = chart_registry.get_available_charts()
            chart_type = st.selectbox("Select Chart Type", available_charts)

            title = st.text_input("Window Title", value="New Chart Window")
            width_label = st.selectbox("Window Width", list(WIDTH_OPTIONS.keys()))
            width_value = WIDTH_OPTIONS[width_label]

            allowed_sources = chart_registry.get_chart_data_sources(chart_type)
            accepts_custom = chart_registry.chart_accepts_custom(chart_type)

            data_keys = allowed_sources.copy()
            if accepts_custom:
                data_keys += state.get_custom_data_keys()

            if not data_keys:
                st.warning("No available data sources for this chart.")
                return

            data_key = st.selectbox("Select Data Source", data_keys)

            if st.button("Add Window"):
                windows = state.get("dashboard_windows")

                new_window = {
                    "id": f"{chart_type}_{len(windows)+1}",
                    "title": title,
                    "type": chart_type,
                    "width": width_value,
                    "data_key": data_key
                }

                windows.append(new_window)
                state.set("dashboard_windows", windows)
                st.success("Window Added!")

        elif mode == "Existing Windows":
            st.subheader("Existing Windows")

            windows = state.get("dashboard_windows")

            if not windows:
                st.info("No windows open.")
            else:
                for index, window in enumerate(windows):
                    with st.container():
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.write(f"📊 **{window['title']}** (Type: `{window['type']}`, Width: {window['width']}/12, Data: `{window['data_key']}`)")

                        with col2:
                            if st.button("Delete", key=f"delete_{window['id']}"):
                                windows.pop(index)
                                state.set("dashboard_windows", windows)
                                st.rerun()

        elif mode == "Configure Chart":
            st.subheader("Configure Chart Settings")

            windows = state.get("dashboard_windows")
            if not windows:
                st.info("No charts to configure.")
                return

            window_ids = [win["id"] for win in windows]
            selected_id = st.selectbox("Select Chart", window_ids)

            target = next((w for w in windows if w["id"] == selected_id), None)
            if not target:
                st.warning("Window not found.")
                return

            df = state.get(target["data_key"])
            if df is None or not isinstance(df, pd.DataFrame):
                st.warning("No data for selected chart.")
                return

            config_ui = chart_registry.get_chart_config_ui(target["type"])
            if config_ui:
                config_ui(df, target)
            else:
                st.info("This chart has no configurable options.")
