# components/spmf/algorithm_registry.py

# 注册所有可用算法
ALGORITHMS = {
    "PrefixSpan": {
        "id": "PrefixSpan",
        "parameters": ["min_support"],
    },
    "GSP": {
        "id": "GSP",
        "parameters": ["min_support"],
    },
    "SPADE": {
        "id": "SPADE",
        "parameters": ["min_support"],
    },
    "CM-SPADE": {
        "id": "CM-SPADE",
        "parameters": ["min_support"],
    },
    "SPAM": {
        "id": "SPAM",
        "parameters": ["min_support", "max_pattern_length"],
    },
    "CM-SPAM": {
        "id": "CM-SPAM",
        "parameters": ["min_support"],
    },
    "Fast": {
        "id": "Fast",
        "parameters": ["min_support", "max_support"],
    },
    "LAPIN": {
        "id": "LAPIN",
        "parameters": ["min_support"],
    },
    "ClaSP": {
        "id": "ClaSP",
        "parameters": ["min_support"],
    },
    "CM-ClaSP": {
        "id": "CM-ClaSP",
        "parameters": ["min_support"],
    },
    "CloFast": {
        "id": "CloFast",
        "parameters": ["min_support", "max_support"],
    },
    "CloSpan": {
        "id": "CloSpan",
        "parameters": ["min_support"],
    },
    "BIDE+": {
        "id": "BIDE+",
        "parameters": ["min_support"],
    },
    "MaxSP": {
        "id": "MaxSP",
        "parameters": ["min_support"],
    },
    "VMSP": {
        "id": "VMSP",
        "parameters": ["min_support"],
    },
    "FEAT": {
        "id": "FEAT",
        "parameters": ["min_support"],
    },
    "FSGP": {
        "id": "FSGP",
        "parameters": ["min_support"],
    },
    "VGEN": {
        "id": "VGEN",
        "parameters": ["min_support"],
    },
    "TKS": {
        "id": "TKS",
        "parameters": ["top_k"],
    },
    "TSP_nonClosed": {
        "id": "TSP_nonClosed",
        "parameters": ["top_k"],
    },
}

def get_available_algorithms():
    return list(ALGORITHMS.keys())

def get_algorithm_parameters(algorithm_name):
    algo = ALGORITHMS.get(algorithm_name)
    if algo:
        return algo.get("parameters", [])
    return []

def get_algorithm_id(algorithm_name):
    algo = ALGORITHMS.get(algorithm_name)
    if algo:
        return algo.get("id")
    return None
