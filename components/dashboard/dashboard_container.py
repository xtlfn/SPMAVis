# components/dashboard/dashboard_container.py

import streamlit as st
import components.state_manager as state
import components.dashboard.chart_registry as chart_registry

def render_dashboard():
    state.init_state()

    windows = state.get("dashboard_windows")

    if not windows:
        st.info("No windows open. Use Sidebar to add charts.")
        return

    row = []
    row_width = 0

    def render_window(window):
        title = window.get("title", "Untitled Window")
        chart_type = window.get("type")
        data_key = window.get("data_key")

        st.markdown(f"### {title}")

        chart_renderer = chart_registry.get_chart_renderer(chart_type)

        if chart_renderer:
            chart_renderer(data_key)
        else:
            st.warning(f"Unknown chart type: {chart_type}")

        st.markdown("---")

    for window in windows:
        w = window.get("width", 6)

        if row_width + w > 12:
            cols = st.columns([r.get("width", 6) for r in row])
            for col, win in zip(cols, row):
                with col:
                    render_window(win)

            row = []
            row_width = 0

        row.append(window)
        row_width += w

    if row:
        cols = st.columns([r.get("width", 6) for r in row])
        for col, win in zip(cols, row):
            with col:
                render_window(win)
