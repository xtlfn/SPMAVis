# components/dashboard/chart_registry.py

from components.dashboard import (
    chart_table,
    chart_bar,
    chart_map,
    chart_spmf,
    chart_spmf_sankey,
    chart_spmf_heatmap
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
    "chart_spmf": {
        "renderer": chart_spmf.render,
        "config_ui": chart_spmf.render_config_ui,
        "fixed_sources": [],
        "accepts_custom_data": True
    },
    "chart_spmf_sankey": {
        "renderer": chart_spmf_sankey.render,
        "config_ui": chart_spmf_sankey.render_config_ui,
        "fixed_sources": [],
        "accepts_custom_data": True
    },
    "chart_spmf_heatmap": {
        "renderer": chart_spmf_heatmap.render,
        "config_ui": chart_spmf_heatmap.render_config_ui,
        "fixed_sources": [],
        "accepts_custom_data": True
    }
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
    return CHARTS.get(chart_type, {}).get("config_ui", None)
