# components/dashboard/chart_rule_list.py

import streamlit as st
import components.state_manager as state

DEFAULT_HEIGHT = 420

def render(data_key=None, settings=None):
    df = state.get(data_key)
    if df is None:
        st.warning("No rule data available.")
        return

    cfg = settings or {}
    try:
        top_k = int(cfg.get("top_k", 10))
    except:
        top_k = 10
    height = cfg.get("height", DEFAULT_HEIGHT)

    if "Support" not in df.columns:
        st.warning("Rule data must include a 'Support' column.")
        return

    df_sorted = df.sort_values("Support", ascending=False).head(top_k)

    lines = []
    for idx, row in enumerate(df_sorted.itertuples(), start=1):
        sup = getattr(row, "Support", "")
        antecedent = getattr(row, "Antecedent", "")
        consequent = getattr(row, "Consequent", "")
        ants = [a.strip() for a in antecedent.split(" & ")]
        cons = [c.strip() for c in consequent.split(" & ")]
        pills = []
        for itm in ants + cons:
            pills.append(
                f"<span style='display:inline-block;"
                "background-color:#e0f3ff;border:1px solid #90caff;"
                "border-radius:10px;padding:4px 8px;margin-right:4px;'>"
                f"{itm}</span>"
            )
        line_html = (
            f"<div style='margin-bottom:12px;'>"
            f"<strong>{idx}.</strong>&nbsp;"
            + "".join(pills)
            + f"&nbsp;<em style='color:#666;'>(support: {sup})</em>"
            "</div>"
        )
        lines.append(line_html)

    container = (
        f"<div style='height:{height}px;overflow:auto;padding-right:10px;'>"
        + "".join(lines) +
        "</div>"
    )
    st.markdown(container, unsafe_allow_html=True)

def render_config_ui(df, window):
    cfg = window.get("settings", {}) or {}
    current_k = cfg.get("top_k", 10)

    top_k = st.number_input(
        "Top K rules to display",
        min_value=1,
        max_value=200,
        value=int(current_k),
        key=f"{window['id']}_topk"
    )

    height = st.number_input(
        "Height (px)",
        min_value=200,
        max_value=1200,
        value=cfg.get("height", DEFAULT_HEIGHT),
        key=f"{window['id']}_height"
    )

    if st.button("Save Chart Settings", key=f"save_{window['id']}"):
        window["settings"] = {
            "top_k": int(top_k),
            "height": int(height)
        }
        st.success("Settings saved.")