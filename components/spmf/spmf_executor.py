import subprocess
import components.spmf.algorithm_registry as registry
import components.state_manager as state
import pandas as pd
import tempfile

def generate_command(algorithm_name, input_file, output_file, parameters):
    algo_id = registry.get_algorithm_id(algorithm_name)
    if algo_id is None:
        raise ValueError(f"Algorithm {algorithm_name} not found")

    param_list = []
    for param_key in registry.get_algorithm_parameters(algorithm_name):
        param_value = parameters.get(param_key)
        if param_value is not None:
            param_list.append(str(param_value))

    command = ["java", "-jar", "components/spmf/spmf.jar", "run", algo_id, input_file, output_file] + param_list
    return command

def run_spmf(algorithm_name, input_file, parameters):
    tmp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
    output_file_path = tmp_output.name
    tmp_output.close()

    command = generate_command(algorithm_name, input_file, output_file_path, parameters)

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"SPMF Error: {result.stderr}")

    # 解析SPMF输出为DataFrame
    df_result = parse_spmf_output(output_file_path)

    # 保存结果
    state.set("spmf_output_data", df_result)

    return df_result

def parse_spmf_output(file_path):
    rows = []
    with open(file_path, "r", encoding="utf-8") as f:
        for pattern_id, line in enumerate(f, start=1):
            parts = line.strip().split(" -1 ")
            row_data = {"Pattern ID": pattern_id}

            # 解析support
            if parts[-1].startswith("#SUP:"):
                support = parts.pop(-1).replace("#SUP:", "").strip()
                row_data["Support"] = support
            else:
                row_data["Support"] = None

            # 解析Itemsets
            for idx, itemset in enumerate(parts):
                if itemset.strip() == "":
                    continue
                items = itemset.strip().split()
                row_data[f"Itemset {idx + 1}"] = ", ".join(items)

            rows.append(row_data)

    df = pd.DataFrame(rows)
    return df
