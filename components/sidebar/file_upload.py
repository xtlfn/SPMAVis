# components/sidebar/file_upload.py

import streamlit as st
import components.state_manager as state
import components.data_ops as ops

def render_file_upload():
    with st.expander("📁 File Upload", expanded=False):
        uploaded_file = st.file_uploader("Select CSV/TXT File", type=["csv", "txt"])
        if uploaded_file:
            st.write(f"**Uploaded File:** {uploaded_file.name}")
            if st.button("Load Data"):
                try:
                    df = ops.load_csv(uploaded_file)
                    state.set("base_data", df)
                    st.success("Base data loaded successfully!")
                except Exception as e:
                    st.error(f"Failed to load data: {e}")
