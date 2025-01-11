import pandas as pd
import streamlit as st
import subprocess

def load_data(file_path):
    try:
        rows = []
        possible_delimiters = ["\t", " ", ",", ";"]

        # 尝试每个分隔符，手动解析每行，确保列数一致
        with open(file_path, "r") as f:
            lines = f.readlines()

        # 统计最长的列数作为基准
        max_columns = 0
        for line in lines[:50]:  # 只处理前 50 行
            for delim in possible_delimiters:
                fields = line.strip().split(delim)
                if len(fields) > max_columns:
                    max_columns = len(fields)
                    best_delim = delim

        # 重新用最佳分隔符解析文件
        for line in lines[:50]:
            fields = line.strip().split(best_delim)
            # 补齐列数不足的行
            while len(fields) < max_columns:
                fields.append("")  # 填充空字符串
            rows.append(fields)

        # 创建 DataFrame
        df = pd.DataFrame(rows, columns=[f"Column {i+1}" for i in range(max_columns)])
        return df

    except Exception as e:
        return f"Error reading file: {e}"
    

def load_output_data(file_path):
    try:
        rows = []
        with open(file_path, "r") as f:
            lines = f.readlines()

        for line in lines:
            fields = line.strip().split()  # 分割每一行数据
            sup_index = [i for i, val in enumerate(fields) if "#SUP:" in val]  # 找到SUP的位置

            if sup_index:
                sup_position = sup_index[0]
                sup_value = fields[sup_position + 1]  # 获取 #SUP: 后面的值
                pattern = " ".join(fields[:sup_position])  # 提取 pattern
                rows.append({"Pattern": pattern, "Support Count": int(sup_value)})
            else:
                rows.append({"Pattern": " ".join(fields), "Support Count": None})

        # 将行数据转换为 DataFrame
        df = pd.DataFrame(rows)
        return df

    except Exception as e:
        return f"Error reading file: {e}"
    

def run_spmf_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            st.success("Run Successful!")
            st.write("Command Output:")
            st.code(result.stdout)  # 结果输出到界面
        else:
            st.error(f"Error: {result.stderr}")
            st.write(f"Command Failed with Return Code: {result.returncode}")
    except Exception as e:
        st.error(f"Exception occurred: {str(e)}")