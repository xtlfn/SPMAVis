import streamlit as st
import os
import tempfile
from algorithm_config import algorithms, generate_parameters_input, generate_spmf_command


# Side Bar
with st.sidebar:
    st.header('SPMAVis')

    # Uploader
    with st.expander("📁 File Input", expanded=True):
        uploaded_file = st.file_uploader("Select File Input", type=["txt", "csv", "xml"], label_visibility="collapsed")

        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
                temp_file.write(uploaded_file.getbuffer()) 
                st.session_state["temp_file_upload_path"] = temp_file.name

            st.write(f"临时文件路径：{st.session_state['temp_file_upload_path']}")  # For Debugging

    # Parameters
    with st.expander("⚙️ Parameters", expanded=True):
        selected_name = st.selectbox("Select Algorithm", list(algorithms.keys()))
        algorithm_id = algorithms[selected_name]["id"]

        parameters = generate_parameters_input(selected_name)

        # see if file uploaded
        if "temp_file_upload_path" in st.session_state:
            uploaded_file = st.session_state["temp_file_upload_path"]  # 从 session_state
        else:
            st.warning("Please Upload a File")
            uploaded_file = None

        output_file = "output.txt"

        if uploaded_file and st.button("Run"):
            try:
                command = generate_spmf_command(algorithm_id, uploaded_file, output_file, parameters)
                os.system(command)
                st.success("Run Successful!")
            except ValueError as e:
                st.error(str(e))


#main Page

st.title("文件读取与表格展示")