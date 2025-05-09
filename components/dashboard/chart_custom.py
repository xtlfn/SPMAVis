# components/dashboard/chart_custom.py

import streamlit as st

def render(data=None):
    if data is not None:
        st.dataframe(data)
    st.write("📊 This is a custom chart placeholder.")
    st.line_chart({"data": [1, 3, 2, 4]})  # 示例图，你可以改成Plotly等