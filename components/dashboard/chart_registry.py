# components/dashboard/chart_registry.py

from components.dashboard import chart_custom, chart_table

# 所有可用图表的注册表
CHARTS = {
    "chart_custom": {
        "renderer": chart_custom.render,
        "data_sources": ["preprocessed_data", "spmf_output_data"],
    },
    "chart_table": {
        "renderer": chart_table.render,
        "data_sources": ["uploaded_file", "preprocessed_data", "spmf_formatted_data", "spmf_output_data"],
    }
}

def get_chart_renderer(chart_type):
    """获取图表渲染函数"""
    return CHARTS.get(chart_type, {}).get("renderer")

def get_available_charts():
    """获取所有图表类型"""
    return list(CHARTS.keys())

def get_chart_data_sources(chart_type):
    """获取图表类型允许的数据源"""
    return CHARTS.get(chart_type, {}).get("data_sources", [])

def get_all_data_sources():
    """获取所有可能的数据源（用于辅助Chart Manager构建下拉列表等）"""
    sources = set()
    for chart in CHARTS.values():
        sources.update(chart.get("data_sources", []))
    return list(sources)
