import streamlit as st
import os
import tempfile
import components.state_manager as state
import components.sidebar.file_upload as file_upload
import components.sidebar.chart_manager as chart_manager
import components.dashboard.dashboard_container as dashboard

st.set_page_config(page_title="SPMAVis", layout="wide")

with st.sidebar:
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image('./static/Logo.png', width=80)
    with col2:
        st.header('SPMAVis')

    file_upload.render_file_upload()

    chart_manager.render_window_manager()

dashboard.render_dashboard()
