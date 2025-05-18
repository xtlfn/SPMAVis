# components/dashboard/chart_rule_network.py

import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import components.state_manager as state
import pandas as pd

DEFAULT_HEIGHT = 420

def render(data_key=None, settings=None):
    df = state.get(data_key)
    if not isinstance(df, pd.DataFrame) or df.empty:
        st.warning("Please select *_summary data source first.")
        return

    settings = settings or {}
    height = settings.get("height", DEFAULT_HEIGHT)

    G = nx.DiGraph()
    for _, row in df.iterrows():
        ant_items = row["Antecedent"].split(" & ")
        cons_items = row["Consequent"].split(" & ")
        weight = row["Support"]
        for a in ant_items:
            for c in cons_items:
                G.add_edge(a, c, weight=weight)

    pos = nx.spring_layout(G, k=0.8, seed=42)

    edge_x, edge_y = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    node_x, node_y, texts = [], [], []
    for n in G.nodes():
        x, y = pos[n]
        node_x.append(x)
        node_y.append(y)
        texts.append(n)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color="#888"),
        hoverinfo="none",
        mode="lines"
    )

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        hoverinfo="text",
        marker=dict(size=10, color="#1f77b4"),
        text=texts,
        textposition="top center"
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title="Association Rule Network",
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        height=height
    )

    st.plotly_chart(fig, use_container_width=True)

def render_config_ui(df, window):
    st.markdown("#### Configure Rule Network Chart")

    height = st.number_input(
        "Height (px)",
        min_value=200,
        max_value=1200,
        value=window.get("settings", {}).get("height", DEFAULT_HEIGHT),
        key=f"{window['id']}_height"
    )

    if st.button("Save Chart Settings", key=f"save_{window['id']}"):
        settings = window.get("settings", {}) or {}
        settings["height"] = height
        window["settings"] = settings
        st.success("Settings saved.")