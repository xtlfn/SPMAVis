import streamlit as st
import plotly.graph_objects as go
from collections import defaultdict
import components.state_manager as state

def render(data_key, settings=None):
    settings = settings or {}
    min_link = settings.get("min_link", 1)
    fields = settings.get("fields", None)

    patterns = state.get(data_key)
    if not isinstance(patterns, list) or not patterns:
        st.warning("No patterns found. Select a '*_patterns' data source.")
        return

    link_counter = defaultdict(int)
    for pattern in patterns:
        support = pattern.get("support", 1) or 1
        for itemset in pattern.get("sequence", []):
            items = list(set(itemset))
            for i in range(len(items)):
                for j in range(i + 1, len(items)):
                    a, b = items[i], items[j]
                    if fields:
                        if a.split("=", 1)[0] not in fields or b.split("=", 1)[0] not in fields:
                            continue
                    link_counter[(a, b)] += support

    filtered = {k: v for k, v in link_counter.items() if v >= min_link}
    if not filtered:
        st.info("No links above threshold.")
        return

    labels = []
    index_map = {}
    def get_index(lbl):
        if lbl not in index_map:
            index_map[lbl] = len(labels)
            labels.append(lbl)
        return index_map[lbl]

    sources, targets, values = [], [], []
    for (a, b), v in filtered.items():
        sources.append(get_index(a))
        targets.append(get_index(b))
        values.append(v)

    fig = go.Figure(data=[go.Sankey(
        node=dict(label=labels, pad=10, thickness=10),
        link=dict(source=sources, target=targets, value=values)
    )])
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

def render_config_ui(df, window):
    st.markdown("**Sankey Settings**")
    settings = window.setdefault("settings", {})
    settings["min_link"] = st.slider(
        "Minimum link support", 0, 100, settings.get("min_link", 1)
    )
    all_fields = sorted({
        item.split("=", 1)[0]
        for p in state.get(window["data_key"]) or []
        for seq in p.get("sequence", [])
        for item in seq if "=" in item
    })
    settings["fields"] = st.multiselect(
        "Fields to include", all_fields, default=settings.get("fields", all_fields)
    )
    if st.button("Save Sankey Settings"):
        st.success("Settings saved.")
