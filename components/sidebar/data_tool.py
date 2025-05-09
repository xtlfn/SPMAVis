import streamlit as st
import pandas as pd
import components.state_manager as state

def render_data_tool():
    with st.expander("🛠️ Data Tool", expanded=False):

        all_keys = state.get_all_keys()
        selected_key = st.selectbox("Select Data Source to Edit", all_keys)

        data = state.get(selected_key)
        if data is None or not isinstance(data, pd.DataFrame):
            st.warning("Selected data is not a valid DataFrame.")
            return

        columns_to_keep = st.multiselect("Select Columns to Keep", data.columns.tolist(), default=data.columns.tolist())
        filtered_df = data[columns_to_keep].copy()

        save_as = st.text_input("Save as (Custom Name)", value="my_data")

        if st.button("Save Processed Data"):
            state.set(save_as, filtered_df)
            state.add_custom_data_key(save_as)

            # 自动创建 chart_table 窗口
            windows = state.get("dashboard_windows")
            new_window = {
                "id": f"table_custom_{len(windows)+1}",
                "title": f"Custom Table: {save_as}",
                "type": "chart_table",
                "width": 6,  # 50%
                "data_key": save_as
            }
            windows.append(new_window)
            state.set("dashboard_windows", windows)

            st.success(f"Saved as `{save_as}` and added to dashboard.")
