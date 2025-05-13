# components/sidebar/chart_manager.py

import streamlit as st
import uuid
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
        mode = st.selectbox("Mode", ["Add New Window", "Existing Windows", "Configure Chart"])

        if mode == "Add New Window":
            st.subheader("Add New Window")
            chart_type = st.selectbox("Select Chart Type", chart_registry.get_available_charts())
            title = st.text_input("Window Title", value="New Chart Window")
            width_label = st.selectbox("Window Width", list(WIDTH_OPTIONS.keys()))
            width_value = WIDTH_OPTIONS[width_label]

            # 固定数据源
            fixed = chart_registry.get_chart_data_sources(chart_type)
            # 动态数据源
            dynamic = state.get_dynamic_data_keys()
            if chart_type.startswith("chart_spmf"):
                dyn = [e["key"] for e in dynamic if e["category"]=="spmf"]
            else:
                dyn = [e["key"] for e in dynamic if e["category"]=="normal"]

            data_keys = fixed + dyn
            if not data_keys:
                st.warning("No available data sources for this chart.")
                return

            data_key = st.selectbox("Select Data Source", data_keys)

            if st.button("Add Window"):
                windows = state.get("dashboard_windows")
                unique_id = f"{chart_type}_{uuid.uuid4().hex[:8]}"
                new_window = {
                    "id": unique_id,
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
                for idx, window in enumerate(windows):
                    col1, col2 = st.columns([3,1])
                    name = f"{window['title']} ({window['id']})"
                    with col1:
                        st.write(f"📊 **{name}**  Type:`{window['type']}`, Data:`{window['data_key']}`")
                    with col2:
                        if st.button("Delete", key=f"del_{window['id']}"):
                            windows.pop(idx)
                            state.set("dashboard_windows", windows)
                            st.rerun()

        elif mode == "Configure Chart":
            st.subheader("Configure Chart Settings")
            windows = state.get("dashboard_windows")
            if not windows:
                st.info("No charts to configure.")
                return
            labels = [f"{w['title']} ({w['id']})" for w in windows]
            sel = st.selectbox("Select Chart", labels)
            sel_id = sel.split("(")[-1].replace(")","")
            target = next((w for w in windows if w["id"]==sel_id), None)
            if not target:
                st.warning("Window not found.")
                return
            df = state.get(target["data_key"])
            if df is None:
                st.warning("No data for selected chart.")
                return
            config_ui = chart_registry.get_chart_config_ui(target["type"])
            if config_ui:
                config_ui(df, target)
            else:
                st.info("This chart has no configurable options.")
