# components/spmf/executor.py
import subprocess
import tempfile
import pandas as pd

import components.spmf.algorithm_registry as registry
import components.spmf.spmf_parser as parser
import components.state_manager as state


# ------------- helper --------------------------------------------------------
_SEQ_ALGOS = {
    "PrefixSpan", "GSP", "SPADE", "CM-SPADE", "SPAM", "CM-SPAM", "Fast", "LAPIN",
    "ClaSP", "CM-ClaSP", "CloFast", "CloSpan", "BIDE+", "MaxSP", "VMSP",
    "FEAT", "FSGP", "VGEN", "TKS", "TSP_nonClosed",
}

_RULE_ALGOS = {"TopKClassRules"}


def _generate_command(algo_name: str, input_file: str, output_file: str, params: dict) -> list[str]:
    algo_id = registry.get_algorithm_id(algo_name)
    if algo_id is None:
        raise ValueError(f"Algorithm {algo_name} not found")

    # registry defines correct order of parameters
    param_list = []
    for key in registry.get_algorithm_parameters(algo_name):
        val = params.get(key)
        if val is not None:
            param_list.append(str(val))

    return ["java", "-jar", "components/spmf/spmf.jar", "run", algo_id, input_file, output_file] + param_list


# ------------- public API ----------------------------------------------------
def run_spmf(algo_name: str, input_file: str, parameters: dict) -> pd.DataFrame:
    tmp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
    output_path = tmp_out.name
    tmp_out.close()

    cmd = _generate_command(algo_name, input_file, output_path, parameters)

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"SPMF Error: {proc.stderr}")

    if algo_name in _RULE_ALGOS:
        df_result = parser.parse_rule_output(output_path, state.get("spmf_dictionary"))
    else:
        df_result = parser.parse_sequence_output(output_path)

    state.set("spmf_output_data", df_result)
    return df_result