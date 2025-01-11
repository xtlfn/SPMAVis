import streamlit as st
import os
import subprocess
import tempfile
import pandas as pd
from algorithm_config import algorithms, generate_parameters_input, generate_spmf_command
from utils import load_data, load_output_data, run_spmf_command

# 初始化 session_state
if "file_info" not in st.session_state:
    st.session_state["file_info"] = {}

# Side Bar
with st.sidebar:
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image('./static/Logo.png', width=80)
    with col2:
        st.header('SPMAVis')

    # Uploader
    with st.expander("📁 File Input", expanded=True):
        uploaded_file = st.file_uploader("Select File Input", type=["txt", "csv", "xml"], label_visibility="collapsed")

        if uploaded_file is not None:
            # 临时保存上传文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
                temp_file.write(uploaded_file.getbuffer())
                input_file_path = temp_file.name

            # 基于上传文件名生成唯一输出文件路径
            output_file_path = input_file_path.replace(".txt", "_output.txt")

            # 保存路径到 session_state
            st.session_state["file_info"]["input_file"] = input_file_path
            st.session_state["file_info"]["output_file"] = output_file_path

    # Parameters
    with st.expander("⚙️ Parameters", expanded=True):
        selected_name = st.selectbox("Select Algorithm", list(algorithms.keys()))
        algorithm_id = algorithms[selected_name]["id"]

        parameters = generate_parameters_input(selected_name)

        if "file_info" in st.session_state and "input_file" in st.session_state["file_info"]:
            uploaded_file = st.session_state["file_info"]["input_file"]
            output_file = st.session_state["file_info"]["output_file"]
        else:
            st.warning("Please Upload a File")
            uploaded_file = None
            output_file = None

        if uploaded_file and st.button("Run"):
            try:
                # 生成命令并执行
                command = generate_spmf_command(algorithm_id, uploaded_file, output_file, parameters)
                run_spmf_command(command)
                st.success("Run Successful!")

            except ValueError as e:
                st.error(str(e))

#main Page

user_message = st.text_input("NLP Intereactions", placeholder="Type your message here...")

col1, col2 = st.columns([2, 2])

# 图表1 - Input File Table
with col1:
    st.caption("Input File Table")
    if "file_info" in st.session_state and "input_file" in st.session_state["file_info"]:
        input_file_path = st.session_state["file_info"]["input_file"]
        if os.path.exists(input_file_path):
            input_data = load_data(input_file_path)
            if isinstance(input_data, pd.DataFrame):
                st.dataframe(input_data, use_container_width=True, height=300)
            else:
                st.error(input_data)  # 显示错误信息
        else:
            st.warning("Input file path not found.")
    else:
        st.warning("No input file uploaded.")

# 图表2 - Output File Table
with col2:
    st.caption("Output File Table")
    if "file_info" in st.session_state and "output_file" in st.session_state["file_info"]:
        output_file_path = st.session_state["file_info"]["output_file"]
        if os.path.exists(output_file_path):
            output_data = load_output_data(output_file_path)
            if isinstance(output_data, pd.DataFrame):
                st.dataframe(output_data, use_container_width=True, height=300)
            else:
                st.error(output_data)  # 显示错误信息
        else:
            st.warning("Output file path not found.")
    else:
        st.warning("No output file generated.")

st.markdown("---")  # 分隔线

# 图表3和图表4的占位行
col3, col4 = st.columns([2, 2])

# 图表3 占位内容
with col3:
    st.caption("Placeholder for Chart 3")
    st.empty()  # 空占位符

# 图表4 占位内容
with col4:
    st.caption("Placeholder for Chart 4")
    st.empty()  # 空占位符
