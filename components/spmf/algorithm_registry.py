# components/spmf/algorithm_registry.py

ALGORITHMS: dict[str, dict] = {
    # -------- sequential pattern mining --------
    "PrefixSpan":    {"id": "PrefixSpan",    "category": "seq",  "parameters": ["min_support"]},
    "GSP":           {"id": "GSP",           "category": "seq",  "parameters": ["min_support"]},
    "SPADE":         {"id": "SPADE",         "category": "seq",  "parameters": ["min_support"]},
    "CM-SPADE":      {"id": "CM-SPADE",      "category": "seq",  "parameters": ["min_support"]},
    "SPAM":          {"id": "SPAM",          "category": "seq",  "parameters": ["min_support", "max_pattern_length"]},
    "CM-SPAM":       {"id": "CM-SPAM",       "category": "seq",  "parameters": ["min_support"]},
    "Fast":          {"id": "Fast",          "category": "seq",  "parameters": ["min_support", "max_support"]},
    "LAPIN":         {"id": "LAPIN",         "category": "seq",  "parameters": ["min_support"]},
    "ClaSP":         {"id": "ClaSP",         "category": "seq",  "parameters": ["min_support"]},
    "CM-ClaSP":      {"id": "CM-ClaSP",      "category": "seq",  "parameters": ["min_support"]},
    "CloFast":       {"id": "CloFast",       "category": "seq",  "parameters": ["min_support", "max_support"]},
    "CloSpan":       {"id": "CloSpan",       "category": "seq",  "parameters": ["min_support"]},
    "BIDE+":         {"id": "BIDE+",         "category": "seq",  "parameters": ["min_support"]},
    "MaxSP":         {"id": "MaxSP",         "category": "seq",  "parameters": ["min_support"]},
    "VMSP":          {"id": "VMSP",          "category": "seq",  "parameters": ["min_support"]},
    "FEAT":          {"id": "FEAT",          "category": "seq",  "parameters": ["min_support"]},
    "FSGP":          {"id": "FSGP",          "category": "seq",  "parameters": ["min_support"]},
    "VGEN":          {"id": "VGEN",          "category": "seq",  "parameters": ["min_support"]},
    "TKS":           {"id": "TKS",           "category": "seq",  "parameters": ["top_k"]},
    "TSP_nonClosed": {"id": "TSP_nonClosed", "category": "seq",  "parameters": ["top_k"]},

    # -------- association / class–rule mining --------
    "TopKClassRules": {
        "id": "TopKClassRules",
        "category": "rule",
        "parameters": ["k", "min_conf", "allowed_items"],   # allowed_items: comma-separated list of IDs
    },
}


def get_available_algorithms() -> list[str]:
    return list(ALGORITHMS)


def get_algorithm_parameters(name: str) -> list[str]:
    return ALGORITHMS[name]["parameters"]


def get_algorithm_id(name: str) -> str:
    return ALGORITHMS[name]["id"]


def get_algorithm_cat(name: str) -> str:
    return ALGORITHMS[name]["category"]