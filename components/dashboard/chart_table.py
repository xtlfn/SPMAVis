# components/dashbing/chart_table.py

import streamlit as st
import components.state_manager as state

def render(data_key=None):
    if not data_key:
        st.info("No data source selected for this chart.")
        return

    data = state.get(data_key)

    if data is not None:
        st.dataframe(data)
    else:
        st.warning(f"No data found for key: `{data_key}`.")
