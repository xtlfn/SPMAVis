# components/dashboard/chart_registry.py

from components.dashboard import chart_table, chart_bar

CHARTS = {
    "chart_bar": {
        "renderer": chart_bar.render,
        "config_ui": chart_bar.render_config_ui,
        "fixed_sources": ["uploaded_file", "preprocessed_data"],
        "accepts_custom_data": True
    },
    "chart_table": {
        "renderer": chart_table.render,
        "fixed_sources": ["uploaded_file", "preprocessed_data", "spmf_formatted_data", "spmf_output_data"],
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

def get_all_data_sources():
    sources = set()
    for chart in CHARTS.values():
        sources.update(chart.get("fixed_sources", []))
    return list(sources)

def get_chart_config_ui(chart_type):
    return CHARTS.get(chart_type, {}).get("config_ui", None)