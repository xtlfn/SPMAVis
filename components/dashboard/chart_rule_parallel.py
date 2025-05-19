# components/dashboard/chart_rule_parallel.py

import streamlit as st
import pandas as pd
import plotly.express as px
import components.state_manager as state

DEFAULT_HEIGHT = 500
def render(data_key=None, settings=None):
    df = state.get(data_key)
    if not isinstance(df, pd.DataFrame) or df.empty:
        st.warning("No rule data available.")
        return

    cfg = settings or {}
    fields   = cfg.get("fields", [])
    min_conf = cfg.get("min_confidence", 0.0)
    height   = cfg.get("height", DEFAULT_HEIGHT)

    if len(fields) < 2:
        st.warning("Select at least two fields in Configure Chart.")
        return

    df_f = df[df["Confidence"] >= min_conf]
    if df_f.empty:
        st.info("No rules pass the confidence threshold.")
        return

    rows = []
    for _, row in df_f.iterrows():
        atoms = [a.strip() for a in row["Antecedent"].split(" & ")]
        mapping = {f: None for f in fields}
        for atom in atoms:
            if "=" in atom:
                attr, val = atom.split("=", 1)
                if attr in fields:
                    mapping[attr] = val
        if any(mapping[f] is None for f in fields):
            continue
        mapping["total_support"] = row["Support"]
        rows.append(mapping)

    combo = pd.DataFrame(rows)
    if combo.empty:
        st.info("No rules contain all selected fields.")
        return

    agg = combo.groupby(fields, as_index=False).agg(total_support=("total_support", "sum"))

    fig = px.parallel_categories(
        agg,
        dimensions=fields,
        color="total_support",
        color_continuous_scale="Blues",
        labels={f: f for f in fields},
        height=height
    )
    fig.update_layout(font=dict(size=12, color="black"))
    st.plotly_chart(fig, use_container_width=True)


def render_config_ui(df, window):
    st.markdown("#### Configure Field Parallel Chart")

    settings = window.get("settings", {}) or {}

    all_fields = sorted({
        atom.split("=", 1)[0]
        for ante in df["Antecedent"]
        for atom in ante.split(" & ")
        if "=" in atom
    })

    saved = settings.get("fields", [])
    valid = [f for f in saved if f in all_fields]
    default = valid if valid else all_fields[:2]

    fields = st.multiselect(
        "Select fields (sequence matters)",
        all_fields,
        default=default,
        key=f"{window['id']}_fields"
    )

    min_conf = st.slider(
        "Min Confidence",
        0.0, 1.0,
        value=settings.get("min_confidence", 0.0),
        key=f"{window['id']}_min_conf"
    )

    height = st.number_input(
        "Height (px)",
        min_value=200,
        max_value=1200,
        value=settings.get("height", DEFAULT_HEIGHT),
        step=10,
        key=f"{window['id']}_height"
    )

    if st.button("Save Chart Settings", key=f"save_{window['id']}"):
        window["settings"] = {
            "fields": fields,
            "min_confidence": float(min_conf),
            "height": int(height)
        }
        st.success("Settings saved.")