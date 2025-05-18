from components.dashboard import (
    chart_seq_heatmap,
    chart_seq_list,
    chart_seq_parallel,
    chart_seq_sankey,
    chart_rule_network,
    chart_rule_scatter,
    chart_table,
    chart_bar,
    chart_map,
)

CHARTS = {
    "chart_bar": {
        "renderer": chart_bar.render,
        "config_ui": chart_bar.render_config_ui,
        "fixed_sources": ["base_data"],
        "accepts_custom_data": True
    },
    "chart_table": {
        "renderer": chart_table.render,
        "config_ui": None,
        "fixed_sources": ["base_data"],
        "accepts_custom_data": True
    },
    "chart_map": {
        "renderer": chart_map.render,
        "config_ui": chart_map.render_config_ui,
        "fixed_sources": ["base_data"],
        "accepts_custom_data": True
    },

    # association rule mining charts
    "chart_rule_scatter": {
        "renderer": chart_rule_scatter.render,
        "config_ui": chart_rule_scatter.render_config_ui,
        "pattern_cat": "rule",
        "fixed_sources": [],
        "accepts_custom_data": True,
    },
    "chart_rule_network": {
        "renderer": chart_rule_network.render,
        "config_ui": chart_rule_network.render_config_ui,
        "pattern_cat": "rule",
        "fixed_sources": [],
        "accepts_custom_data": True,
    },

    # Sequential Pattern Mining Charts
    "chart_seq_list": {
        "renderer": chart_seq_list.render,
        "config_ui": chart_seq_list.render_config_ui,
        "pattern_cat": "seq",
        "fixed_sources": [],
        "accepts_custom_data": True,
    },
    "chart_seq_sankey": {
        "renderer": chart_seq_sankey.render,
        "config_ui": chart_seq_sankey.render_config_ui,
        "pattern_cat": "seq",
        "fixed_sources": [],
        "accepts_custom_data": True,
    },
    "chart_seq_heatmap": {
        "renderer": chart_seq_heatmap.render,
        "config_ui": chart_seq_heatmap.render_config_ui,
        "pattern_cat": "seq",
        "fixed_sources": [],
        "accepts_custom_data": True,
    },
    "chart_seq_parallel": {
        "renderer": chart_seq_parallel.render,
        "config_ui": chart_seq_parallel.render_config_ui,
        "pattern_cat": "seq",
        "fixed_sources": [],
        "accepts_custom_data": True,
    },
}

def get_chart_renderer(chart_type):
    return CHARTS.get(chart_type, {}).get("renderer")

def get_available_charts():
    return list(CHARTS.keys())

def get_chart_data_sources(chart_type):
    return CHARTS.get(chart_type, {}).get("fixed_sources", [])

def chart_accepts_custom(chart_type):
    return CHARTS.get(chart_type, {}).get("accepts_custom_data", False)

def get_chart_config_ui(chart_type):
    return CHARTS.get(chart_type, {}).get("config_ui")
