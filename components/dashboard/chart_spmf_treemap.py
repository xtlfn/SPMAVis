import streamlit as st
import plotly.express as px
import pandas as pd
import components.state_manager as state
from collections import Counter


def render(data_key=None, settings=None):
    patterns = state.get(data_key)
    if not isinstance(patterns, list) or not patterns:
        st.warning("No pattern list found. Please select a `*_patterns` data source.")
        return

    cfg = settings or {}
    fields = cfg.get("fields", [])
    if not fields:
        st.warning("Please select at least one field for Treemap.")
        return

    # 1) Accumulate support per hierarchical node
    node_support = Counter()
    parent_map = {}
    for pat in patterns:
        sup = pat.get("support", 0)
        seq_vals = []
        # extract sequential field values until missing
        for fld in fields:
            val = None
            for seq in pat.get("sequence", []):
                for item in seq:
                    if item.startswith(f"{fld}="):
                        val = item.split("=", 1)[1]
                        break
                if val is not None:
                    break
            if val is None:
                break
            seq_vals.append(val)
        # record each node and its parent
        for i, val in enumerate(seq_vals):
            node = f"{fields[i]}={val}"
            parent = ("All Patterns" if i == 0 else f"{fields[i-1]}={seq_vals[i-1]}")
            node_support[node] += sup
            parent_map[node] = parent

    if not node_support:
        st.info("No hierarchical data to display for selected fields.")
        return

    # 2) Build DataFrame for treemap
    total = sum(node_support.values())
    labels = ["All Patterns"] + list(node_support.keys())
    parents = [""] + [parent_map[n] for n in node_support.keys()]
    values = [total] + [node_support[n] for n in node_support.keys()]
    df = pd.DataFrame({"label": labels, "parent": parents, "value": values})

    # 3) Plot Treemap
    fig = px.treemap(
        df,
        names="label",
        parents="parent",
        values="value",
        color="value",
        color_continuous_scale="Blues",
        title="Sequential Pattern Treemap (sum of support)"
    )
    fig.update_layout(margin=dict(l=50, r=50, t=50, b=50))
    st.plotly_chart(fig, use_container_width=True)


def render_config_ui(patterns, window):
    if not isinstance(patterns, list) or not patterns:
        st.info("No patterns data for configuration.")
        return

    seen, options = set(), []
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
        "Select fields (hierarchy) for Treemap",
        options,
        default=selected,
        key=f"{window['id']}_treemap_fields"
    )

    if st.button("Save Treemap Settings", key=f"save_treemap_{window['id']}"):
        if not fields:
            st.error("Please select at least one field.")
        else:
            window["settings"] = {"fields": fields}
            st.success("Settings saved.")
