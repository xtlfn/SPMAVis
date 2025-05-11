#components/state_manager.py

import streamlit as st

DEFAULT_STATE = {
    "uploaded_file": None,
    "preprocessed_data": None,
    "spmf_formatted_file": None,    # 保存SPMF格式 txt 文件路径
    "spmf_dictionary": None,        # 保存Item Dictionary DataFrame
    "spmf_formatted_data": None,    # SPMF转换后的 DataFrame（纯数字）
    "spmf_output_data": None,       # 挖掘结果的 DataFrame
    "spmf_structured_patterns": None,  # SPMF 专用图表结构（List[Dict]）
    "spmf_summary_df": None,           # 可供通用图表使用的 summary DataFrame
    "dashboard_windows": [],
}

# 初始化（如果Session里没有就写入默认值）
def init_state():
    for key, value in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value

# 只允许访问 DEFAULT_STATE 里的 key（标准数据源）
def get(key):
    return st.session_state.get(key)

def set(key, value):
    st.session_state[key] = value

def reset(key):
    if key in DEFAULT_STATE:
        st.session_state[key] = DEFAULT_STATE[key]

def get_all_state():
    return {key: st.session_state.get(key) for key in DEFAULT_STATE}

# --- 动态 key（临时数据或特殊用途，不进入标准数据源列表） ---
def set_dynamic(key, value):
    st.session_state[key] = value

def get_dynamic(key):
    return st.session_state.get(key, None)

def get_all_keys():
    return list(st.session_state.keys())

# --- 自定义数据源 key 的管理（用户保存的 DataFrame 结果） ---
CUSTOM_STATE_LIST_KEY = "_custom_data_keys"

def get_custom_data_keys():
    return st.session_state.get(CUSTOM_STATE_LIST_KEY, [])

def add_custom_data_key(key):
    if CUSTOM_STATE_LIST_KEY not in st.session_state:
        st.session_state[CUSTOM_STATE_LIST_KEY] = []
    if key not in st.session_state[CUSTOM_STATE_LIST_KEY]:
        st.session_state[CUSTOM_STATE_LIST_KEY].append(key)