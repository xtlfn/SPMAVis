import streamlit as st
import components.state_manager as state
import components.sidebar.file_upload as file_upload
import components.sidebar.chart_manager as chart_manager
import components.sidebar.algorithm as algorithm
import components.sidebar.data_tool as data_tool
import components.dashboard.dashboard_container as dashboard

st.set_page_config(page_title="SPMAVis", layout="wide")
state.init_state()

with st.sidebar:
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image('./static/Logo.png', width=80)
    with col2:
        st.header('SPMAVis')

    file_upload.render_file_upload()
    data_tool.render_data_tool()
    chart_manager.render_window_manager()
    algorithm.render_algorithm_panel() 

dashboard.render_dashboard()
