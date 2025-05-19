# components/dashboard/chart_rule_sankey.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import components.state_manager as state

DEFAULT_HEIGHT = 500

def render(data_key=None, settings=None):
    df = state.get(data_key)
    if not isinstance(df, pd.DataFrame) or df.empty:
        st.warning("No rule data available.")
        return

    cfg = settings or {}
    fields = cfg.get("fields", [])
    min_conf = cfg.get("min_confidence", 0.0)
    height = cfg.get("height", DEFAULT_HEIGHT)

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
        if all(mapping[f] is not None for f in fields):
            mapping["value"] = row["Support"]
            rows.append(mapping)

    combo = pd.DataFrame(rows)
    if combo.empty:
        st.info("No rules contain all selected fields.")
        return

    agg = combo.groupby(fields, as_index=False).agg(value=("value", "sum"))

    label_list = []
    for f in fields:
        label_list += list(agg[f].unique())
    labels = []
    for x in label_list:
        if x not in labels:
            labels.append(x)

    idx_map = {label: i for i, label in enumerate(labels)}

    source_idxs = []
    target_idxs = []
    values = []

    for _, row in agg.iterrows():
        for i in range(len(fields) - 1):
            src = idx_map[row[fields[i]]]
            tgt = idx_map[row[fields[i+1]]]
            source_idxs.append(src)
            target_idxs.append(tgt)
            values.append(row["value"])

    sankey = go.Sankey(
        node=dict(
            label=labels,
            pad=15,
            thickness=20,
            color="lightblue",
            line=dict(color="white", width=0)
        ),
        link=dict(
            source=source_idxs,
            target=target_idxs,
            value=values,
            color="rgba(100,100,200,0.4)"
        )
    )

    fig = go.Figure(sankey)
    fig.update_traces(textfont=dict(color="black"), selector=dict(type="sankey"))
    fig.update_layout(
        height=height,
        font=dict(size=12)
    )
    st.plotly_chart(fig, use_container_width=True)

def render_config_ui(df, window):
    st.markdown("#### Configure Rule Sankey Chart")

    settings = window.get("settings", {}) or {}

    all_fields = sorted({
        atom.split("=", 1)[0]
        for ante in df["Antecedent"]
        for atom in ante.split(" & ")
        if "=" in atom
    })
    saved = settings.get("fields", [])
    valid = [f for f in saved if f in all_fields]
    default = valid if len(valid) >= 2 else all_fields[:2]

    fields = st.multiselect(
        "Select fields (flow order)",
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