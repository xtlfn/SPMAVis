import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import components.state_manager as state
import pandas as pd

def render(data_key=None, settings=None):
    df = state.get(data_key)
    if not isinstance(df, pd.DataFrame) or df.empty:
        st.warning("Please select *_summary data source first.")
        return

    G = nx.DiGraph()
    for _, row in df.iterrows():
        ant_items = row["Antecedent"].split(" & ")
        cons_items = row["Consequent"].split(" & ")
        weight = row["Support"]
        for a in ant_items:
            for c in cons_items:
                G.add_edge(a, c, weight=weight)

    pos = nx.spring_layout(G, k=0.8, seed=42)

    edge_x, edge_y, edge_w = [], [], []
    for u, v, dat in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
        edge_w.append(dat["weight"])

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
        title="Association Rule network",
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
    )
    st.plotly_chart(fig, use_container_width=True)

def render_config_ui(df, window):
    st.info("no config options available for this chart.")
