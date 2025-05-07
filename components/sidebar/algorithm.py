import streamlit as st
import os
import components.state_manager as state
import components.spmf.algorithm_registry as registry
import components.spmf.spmf_executor as executor
import components.spmf.spmf_converter as converter

def render_algorithm_panel():
    state.init_state()

    with st.expander("📌 Algorithm Runner", expanded=False):
        st.header("Sequential Pattern Mining")

        # --- SPMF格式文件生成 ---
        st.subheader("SPMF File Preparation")

        df_preprocessed = state.get("preprocessed_data")
        spmf_file = state.get("spmf_formatted_file")

        if df_preprocessed is None:
            st.warning("Please upload and preprocess data first.")
        else:
            if spmf_file:
                st.success("SPMF formatted file already generated.")
                st.write(f"Path: `{spmf_file}`")
            else:
                if st.button("Generate SPMF Format File"):
                    try:
                        spmf_file, _, _ = converter.convert_to_spmf_format()
                        st.success("SPMF file generated successfully.")
                        st.write(f"Path: `{spmf_file}`")
                    except Exception as e:
                        st.error(f"Failed to generate SPMF file: {e}")
                        return

        if not spmf_file:
            st.warning("Please generate SPMF format file before running algorithm.")
            return

        # --- 算法选择 ---
        st.header("Run Mining Algorithm")

        algorithm_list = registry.get_available_algorithms()
        selected_algorithm = st.selectbox("Select Algorithm", algorithm_list)

        if not selected_algorithm:
            st.warning("Please select an algorithm.")
            return

        # --- 参数选择 ---
        parameters = {}
        param_keys = registry.get_algorithm_parameters(selected_algorithm)

        for param in param_keys:
            if param == "min_support":
                parameters[param] = st.slider("Min Support (0.0 to 1.0)", 0.0, 1.0, 0.5, 0.01)
            elif param == "max_support":
                parameters[param] = st.slider("Max Support (0.0 to 1.0)", 0.0, 1.0, 1.0, 0.01)
            elif param == "max_pattern_length":
                parameters[param] = st.number_input("Max Pattern Length", min_value=1, value=100)
            elif param == "top_k":
                parameters[param] = st.number_input("Top-K", min_value=1, value=10)

        # --- 运行按钮 ---
        if st.button("Run Algorithm"):

            with st.spinner("Running Algorithm..."):
                try:
                    result_df = executor.run_spmf(selected_algorithm, spmf_file, parameters)
                    st.success("Algorithm finished successfully!")

                    # 保存 + 展示
                    state.set("spmf_output_data", result_df)

                except Exception as e:
                    st.error(f"Error running algorithm: {e}")
