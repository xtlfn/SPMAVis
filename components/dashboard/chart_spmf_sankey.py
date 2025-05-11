# components/dashboard/chart_spmf_sankey.py

import streamlit as st
import plotly.graph_objects as go
import components.state_manager as state
from collections import defaultdict

def render(data_key=None, settings=None):
    st.subheader("Item Co-occurrence Sankey Diagram")

    patterns = state.get(data_key)
    if not patterns:
        st.warning("No pattern data found.")
        return

    link_counter = defaultdict(int)

    # 构建 item 共现关系（同一个 itemset 内）
    for pattern in patterns:
        support = pattern.get("support", 1)
        for itemset in pattern.get("sequence", []):
            items = list(set(itemset))
            for i in range(len(items)):
                for j in range(i + 1, len(items)):
                    a, b = items[i], items[j]
                    link_counter[(a, b)] += support

    if not link_counter:
        st.info("No valid item relationships to show.")
        return

    # 构建 Sankey 数据
    node_labels = []
    label_to_index = {}

    def get_idx(label):
        if label not in label_to_index:
            label_to_index[label] = len(node_labels)
            node_labels.append(label)
        return label_to_index[label]

    sources, targets, values = [], [], []
    for (a, b), v in link_counter.items():
        src = get_idx(a)
        tgt = get_idx(b)
        sources.append(src)
        targets.append(tgt)
        values.append(v)

    # 节点颜色（亮色循环）
    color_palette = [
        "#6baed6", "#9ecae1", "#c6dbef", "#fdd0a2", "#fc8d59",
        "#d9d9d9", "#bcbddc", "#ef3b2c", "#74c476", "#ffeda0"
    ]
    node_colors = [color_palette[i % len(color_palette)] for i in range(len(node_labels))]

    # 使用灰色连接线
    link_colors = ["rgba(100,150,250,0.5)" for _ in sources]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=10,
            thickness=10,  # 更粗的节点
            line=dict(color="black", width=0.5),
            label=node_labels,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors
        )
    )])

    fig.update_layout(
        paper_bgcolor="white",
        font=dict(size=16, color="black"),  # 字体更小更清晰
        margin=dict(l=40, r=40, t=40, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)

def render_config_ui(df, window):
    st.markdown("This chart shows item co-occurrence within itemsets.")