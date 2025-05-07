import streamlit as st
import os
import tempfile
import pandas as pd
from algorithm_config import algorithms, generate_parameters_input, generate_spmf_command
from utils import load_data, load_output_data, run_spmf_command, add_unique_items_column_from_df
from file_converter import get_supported_formats, convert_file_to_spmf


st.set_page_config(page_title="SPMAVis", layout="wide")

# Session State Initialization
if "file_info" not in st.session_state:
    st.session_state["file_info"] = {}
if "input_data" not in st.session_state:
    st.session_state["input_data"] = None
if "raw_output" not in st.session_state:
    st.session_state["raw_output"] = None
if "processed_output" not in st.session_state:
    st.session_state["processed_output"] = None

# ------------------------- Side bar -------------------------
with st.sidebar:
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image('./static/Logo.png', width=80)
    with col2:
        st.header('SPMAVis')

    with st.expander("📁 File Input", expanded=True):
    # file input
        raw_file = st.file_uploader("Select File Input", type=["txt", "csv"], label_visibility="collapsed")
        if raw_file is not None:
            format_list = get_supported_formats()
            selected_format = st.selectbox("Select Format", format_list)
            if st.button("Confirm"):
                converted_obj = convert_file_to_spmf(raw_file, selected_format)
                if converted_obj:
                    st.session_state["converted_file"] = converted_obj
                    st.success("File successfully converted to SPMF format!")
                else:
                    st.error("Conversion failed. Please check if content matches the chosen format.")

        if "converted_file" in st.session_state and st.session_state["converted_file"] is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
                temp_file.write(st.session_state["converted_file"].getbuffer())
                input_file_path = temp_file.name
            output_file_path = input_file_path.replace(".txt", "_output.txt")
            st.session_state["file_info"]["input_file"] = input_file_path
            st.session_state["file_info"]["output_file"] = output_file_path
            input_data = load_data(input_file_path)
            if hasattr(input_data, "shape"):
                st.session_state["input_data"] = input_data
                st.success("Input data loaded successfully!")
            else:
                st.error("Error loading input data: " + str(input_data))

    # Run Algorithm
    with st.expander("⚙️ Parameters", expanded=True):
        selected_name = st.selectbox("Select Algorithm", list(algorithms.keys()))
        algorithm_id = algorithms[selected_name]["id"]
        parameters = generate_parameters_input(selected_name)
        if st.session_state["file_info"].get("input_file") is not None:
            input_file_path = st.session_state["file_info"]["input_file"]
            output_file_path = st.session_state["file_info"]["output_file"]
        else:
            st.warning("Please Upload a File")
            input_file_path, output_file_path = None, None
        if input_file_path and st.button("Run"):
            st.session_state["processed_output"] = None  
            try:
                command = generate_spmf_command(algorithm_id, input_file_path, output_file_path, parameters)
                run_spmf_command(command)
                st.success("Run Successful!")
                if os.path.exists(output_file_path):
                    raw_output = load_output_data(output_file_path)
                    if isinstance(raw_output, pd.DataFrame):
                        st.session_state["raw_output"] = raw_output
                    else:
                        st.error("Error loading output data: " + str(raw_output))
                else:
                    st.warning("After running, output file not found.")
            except ValueError as e:
                st.error(str(e))

    # Output Postprocessing
    with st.expander("🔧 Output-Postprocessing", expanded=False):
        add_unique = st.checkbox("Add Unique Item Count")
        filter_val = st.number_input("Filter by Mininum Unique Item Count", min_value=0, value=0)
        if st.button("Apply"):
            if st.session_state["raw_output"] is not None:
                df = st.session_state["raw_output"]
                if add_unique or filter_val > 0:
                    df = add_unique_items_column_from_df(df)
                if filter_val > 0:
                    df = df[df["Unique Items"] >= filter_val]
                st.session_state["processed_output"] = df
                st.success("Output postprocessing applied successfully!")
            else:
                st.warning("No raw output available for postprocessing.")

# ------------------------- Main Dashboard -------------------------
user_message = st.text_input("NLP Intereactions", placeholder="Type your message here...")

col1, col2 = st.columns([2, 2])
with col1:
    st.caption("Input File Table")
    if st.session_state["input_data"] is not None:
        st.dataframe(st.session_state["input_data"], use_container_width=True, height=300)
    else:
        st.warning("No input file uploaded.")
with col2:
    st.caption("Output File Table")
    if st.session_state["processed_output"] is not None:
        output_data = st.session_state["processed_output"]
    elif st.session_state["raw_output"] is not None:
        output_data = st.session_state["raw_output"]
    else:
        st.warning("No output file generated.")
        output_data = None
    if output_data is not None:
        st.dataframe(output_data, use_container_width=True, height=300)

st.markdown("---")
col3, col4 = st.columns([2, 2])
with col3:
    st.caption("Placeholder for Chart 3")
    st.empty()
with col4:
    st.caption("Placeholder for Chart 4")
    st.empty()