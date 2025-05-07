import streamlit as st
import components.state_manager as state
import components.dashboard.chart_registry as chart_registry

WIDTH_OPTIONS = {
    "Small (25%)": 3,
    "Medium (50%)": 6,
    "Large (75%)": 9,
    "Full (100%)": 12,
}

def render_window_manager():
    state.init_state()

    with st.expander("📁 Chart Manager", expanded=False):

        st.header("Window Manager")

        mode = st.selectbox("Mode", ["Add New Window", "Existing Windows"])

        if mode == "Add New Window":
            st.subheader("Add New Window")

            available_charts = chart_registry.get_available_charts()
            chart_type = st.selectbox("Select Chart Type", available_charts)

            title = st.text_input("Window Title", value="New Chart Window")
            width_label = st.selectbox("Window Width", list(WIDTH_OPTIONS.keys()))
            width_value = WIDTH_OPTIONS[width_label]

            # 只从 chart_registry 允许的 sources 里选择
            allowed_data_sources = chart_registry.get_chart_data_sources(chart_type)
            data_key = st.selectbox("Select Data Source", allowed_data_sources)

            if st.button("Add Window"):
                windows = state.get("dashboard_windows")

                new_window = {
                    "id": f"{chart_type}_{len(windows)+1}",
                    "title": title,
                    "type": chart_type,
                    "width": width_value,
                    "data_key": data_key
                }

                windows.append(new_window)
                state.set("dashboard_windows", windows)
                st.success("Window Added!")

        elif mode == "Existing Windows":
            st.subheader("Existing Windows")

            windows = state.get("dashboard_windows")

            if not windows:
                st.info("No windows open.")
            else:
                for index, window in enumerate(windows):
                    with st.container():
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.write(f"📊 **{window['title']}** (Type: `{window['type']}`, Width: {window['width']}/12, Data: `{window['data_key']}`)")

                        with col2:
                            if st.button("Delete", key=f"delete_{window['id']}"):
                                windows.pop(index)
                                state.set("dashboard_windows", windows)
                                st.rerun()
