# components/dashboard/chart_spmf_sankey.py

import streamlit as st
import plotly.graph_objects as go
import components.state_manager as state
from collections import defaultdict

def render(data_key=None, settings=None):

    patterns = state.get(data_key)
    if not isinstance(patterns, list) or not patterns:
        st.warning("No pattern list found. Please select a `*_patterns` data source.")
        return

    # Count co-occurrences within each itemset, weighted by support
    link_counter = defaultdict(int)
    for pattern in patterns:
        support = pattern.get("support", 1) or 1
        for itemset in pattern.get("sequence", []):
            items = list(set(itemset))
            for i in range(len(items)):
                for j in range(i + 1, len(items)):
                    a, b = items[i], items[j]
                    link_counter[(a, b)] += support

    if not link_counter:
        st.info("No co-occurrence relationships to display.")
        return

    # Build Sankey data
    node_labels = []
    label_to_index = {}
    sources, targets, values = [], [], []

    def get_idx(label):
        if label not in label_to_index:
            label_to_index[label] = len(node_labels)
            node_labels.append(label)
        return label_to_index[label]

    for (a, b), count in link_counter.items():
        src = get_idx(a)
        tgt = get_idx(b)
        sources.append(src)
        targets.append(tgt)
        values.append(count)

    # Node and link colors
    palette = ["#6baed6", "#9ecae1", "#c6dbef", "#fdd0a2", "#fc8d59"]
    node_colors = [palette[i % len(palette)] for i in range(len(node_labels))]
    link_colors = ["rgba(100,150,250,0.5)" for _ in values]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            label=node_labels,
            color=node_colors,
            pad=10,
            thickness=10,
            line=dict(color="black", width=0.5)
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors
        )
    )])
    fig.update_layout(margin=dict(l=40, r=40, t=40, b=40))

    st.plotly_chart(fig, use_container_width=True)

def render_config_ui(df, window):
    st.info("No configurable options for Sankey diagram.")

