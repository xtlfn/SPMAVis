import streamlit as st

# --- 系统默认可用数据，用于Chart等数据选择 ---
DEFAULT_STATE = {
    "uploaded_file": None,
    "preprocessed_data": None,
    "spmf_formatted_file": None,
    "spmf_output_data": None,
    "dashboard_windows": [],
}

# 初始化（如果Session里没有就写入默认值）
def init_state():
    for key, value in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value

# 只允许访问 DEFAULT_STATE 里的key（标准数据源）
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