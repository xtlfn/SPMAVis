import streamlit as st

algorithms = {
    "PrefixSpan": {"id": "PrefixSpan", "parameter_type1": "min_support"},
    "GSP": {"id": "GSP", "parameter_type1": "min_support"},
    "SPADE": {"id": "SPADE", "parameter_type1": "min_support"},
    "CM-SPADE": {"id": "CM-SPADE", "parameter_type1": "min_support"},
    "SPAM": {"id": "SPAM", "parameter_type1": "min_support", "parameter_type2": "max_pattern_length"},
    "CM-SPAM": {"id": "CM-SPAM", "parameter_type1": "min_support"},
    "Fast": {"id": "Fast", "parameter_type1": "min_support", "parameter_type2": "max_support"},
    "LAPIN": {"id": "LAPIN", "parameter_type1": "min_support"},
    "ClaSP": {"id": "ClaSP", "parameter_type1": "min_support"},
    "CM-ClaSP": {"id": "CM-ClaSP", "parameter_type1": "min_support"},
    "CloFast": {"id": "CloFast", "parameter_type1": "min_support", "parameter_type2": "max_support"},
    "CloSpan": {"id": "CloSpan", "parameter_type1": "min_support"},
    "BIDE+": {"id": "BIDE+", "parameter_type1": "min_support"},
    "MaxSP": {"id": "MaxSP", "parameter_type1": "min_support"},
    "VMSP": {"id": "VMSP", "parameter_type1": "min_support"},
    "FEAT": {"id": "FEAT", "parameter_type1": "min_support"},
    "FSGP": {"id": "FSGP", "parameter_type1": "min_support"},
    "VGEN": {"id": "VGEN", "parameter_type1": "min_support"},
    "TKS": {"id": "TKS", "parameter_type1": "top_k"},
    "TSP_nonClosed": {"id": "TSP_nonClosed", "parameter_type1": "top_k"}
}
import streamlit as st

def generate_parameters_input(algorithm_name):
    parameters = {}
    algo_config = algorithms.get(algorithm_name)
    
    if not algo_config:
        st.error(f"No parameters found for {algorithm_name}")
        return {}

    for key, value in algo_config.items():
        if "parameter_type" in key:
            if value == "min_support":
                parameters["min_support"] = st.slider("Min SUP (0.0 to 1.0)", 0.0, 1.0, 0.5, 0.01)
            elif value == "max_support":
                parameters["max_support"] = st.slider("Max SUP (0.0 to 1.0)", 0.0, 1.0, 1.0, 0.01)
            elif value == "max_pattern_length":
                parameters["max_pattern_length"] = st.number_input("Max Pattern Length", min_value=1, value=100)
            elif value == "top_k":
                parameters["top_k"] = st.number_input("Top-K", min_value=1, value=10)

    return parameters


def generate_spmf_command(algorithm_name, input_file, output_file, parameters):
    algo_config = algorithms.get(algorithm_name)
    if algo_config is None:
        raise ValueError(f"{algorithm_name} Unfound")

    algorithm_id = algo_config["id"]

    command_params = [f"{parameters[value]}" for key, value in algo_config.items() if key.startswith("parameter_type") and value in parameters]

    command = f"java -jar spmf.jar run {algorithm_id} {input_file} {output_file} " + " ".join(command_params)

    return command