#components/state_manager.py

import streamlit as st

DEFAULT_STATE = {
    "base_data": None,
    "dashboard_windows": []
}

CUSTOM_STATE_LIST_KEY = "_dynamic_data_keys"

def init_state():
    for key, value in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if CUSTOM_STATE_LIST_KEY not in st.session_state:
        st.session_state[CUSTOM_STATE_LIST_KEY] = []

def get(key):
    return st.session_state.get(key)

def set(key, value):
    st.session_state[key] = value

def reset(key):
    if key in DEFAULT_STATE:
        st.session_state[key] = DEFAULT_STATE[key]

def get_all_state():
    return {k: st.session_state.get(k) for k in DEFAULT_STATE}

def get_all_keys():
    return list(st.session_state.keys())


def get_dynamic_data_keys():
    return st.session_state.get(CUSTOM_STATE_LIST_KEY, [])

def add_dynamic_data_key(key, category="normal"):
    entry = {"key": key, "category": category}
    if entry not in st.session_state[CUSTOM_STATE_LIST_KEY]:
        st.session_state[CUSTOM_STATE_LIST_KEY].append(entry)
