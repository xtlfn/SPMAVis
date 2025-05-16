# components/dashboard/chart_spmf_sunburst.py

# components/dashboard/chart_spmf_sunburst.py

import streamlit as st
import plotly.graph_objects as go
import components.state_manager as state
from collections import Counter


def render(data_key=None, settings=None):
    """
    Render a Sunburst chart showing hierarchical aggregation of support across selected fields.
    """
    patterns = state.get(data_key)
    if not isinstance(patterns, list) or not patterns:
        st.warning("No pattern list found. Please select a `*_patterns` data source.")
        return

    cfg = settings or {}
    fields = cfg.get("fields", [])
    if not fields:
        st.warning("Please select at least one field in chart configuration.")
        return

    # 1) Build hierarchical support sums
    node_support = Counter()
    parent_map = {}
    for pat in patterns:
        sup = pat.get("support", 0)
        # Extract values in order, stopping at first missing
        values = []
        for fld in fields:
            val = None
            for seq in pat.get("sequence", []):
                for item in seq:
                    if item.startswith(f"{fld}="):
                        val = item.split("=",1)[1]
                        break
                if val is not None:
                    break
            if val is None:
                break
            values.append(val)
        # Accumulate support for each node and record parent
        for i, val in enumerate(values):
            node = f"{fields[i]}={val}"
            parent = f"{fields[i-1]}={values[i-1]}" if i > 0 else ""
            node_support[node] += sup
            parent_map[node] = parent

    if not node_support:
        st.info("No hierarchical data to display for selected fields.")
        return

    # 2) Prepare sunburst lists
    labels = list(node_support.keys())
    parents = [parent_map[l] for l in labels]
    values = [node_support[l] for l in labels]

    # 3) Build Sunburst figure
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues='total',
        marker=dict(colors=values, colorscale='Blues')
    ))
    fig.update_layout(
        margin=dict(l=50, r=50, t=50, b=50),
        title_text="Sequential Pattern Sunburst (sum of support)"
    )
    st.plotly_chart(fig, use_container_width=True)


def render_config_ui(patterns, window):
    """
    Configuration UI: select hierarchical fields for Sunburst.
    """
    if not isinstance(patterns, list) or not patterns:
        st.info("No patterns data for configuration.")
        return

    # Discover available fields
    seen = set()
    options = []
    for pat in patterns:
        for seq in pat.get("sequence", []):
            for item in seq:
                if "=" in item:
                    f, _ = item.split("=", 1)
                    if f not in seen:
                        seen.add(f)
                        options.append(f)
    options.sort()

    cfg = window.get("settings", {}) or {}
    selected = cfg.get("fields", options[:1])

    fields = st.multiselect(
        "Select fields (hierarchical order)",
        options,
        default=selected,
        key=f"{window['id']}_sunburst_fields"
    )

    if st.button("Save Sunburst Settings", key=f"save_sunburst_{window['id']}"):
        if not fields:
            st.error("Please select at least one field.")
        else:
            window["settings"] = {"fields": fields}
            st.success("Settings saved.")
