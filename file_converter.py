import io

SUPPORTED_FORMATS = {
    "csv_comma": {
        "description": "CSV with Comma ',' as separator",
        "parser": "_parse_csv_comma"
    },
    "csv_semicolon": {
        "description": "CSV with Semicolon ';' as separator",
        "parser": "_parse_csv_semicolon"
    },
    "txt_tab": {
        "description": "Text with TAB as separator",
        "parser": "_parse_txt_tab"
    },
    "spmf": {
        "description": "SPMF sequence format (ends with -2)",
        "parser": "_parse_spmf_sequence"
    }
}

def get_supported_formats():
# get list
    return list(SUPPORTED_FORMATS.keys())

def convert_file_to_spmf(file_obj, source_format):
# convert
    content = file_obj.read().decode("utf-8", errors="replace")
    parser_name = SUPPORTED_FORMATS[source_format]["parser"]
    parser_fn = globals().get(parser_name, None)
    if not parser_fn:
        return None
    try:
        spmf_str = parser_fn(content)
        if not spmf_str:
            return None
        return io.BytesIO(spmf_str.encode("utf-8"))
    except:
        return None

def _parse_csv_comma(content_str):
# csv
    lines = content_str.strip().split("\n")
    if not lines:
        return None
    spmf_lines = []
    for line in lines:
        if "," not in line:
            return None
        items = line.split(",")
        spmf_lines.append(" ".join(items) + " -1")
    return "\n".join(spmf_lines)

def _parse_csv_semicolon(content_str):
# semicolon
    lines = content_str.strip().split("\n")
    if not lines:
        return None
    spmf_lines = []
    for line in lines:
        if ";" not in line:
            return None
        items = line.split(";")
        spmf_lines.append(" ".join(items) + " -1")
    return "\n".join(spmf_lines)

def _parse_txt_tab(content_str):
# tab
    lines = content_str.strip().split("\n")
    if not lines:
        return None
    spmf_lines = []
    for line in lines:
        if "\t" not in line:
            return None
        items = line.split("\t")
        spmf_lines.append(" ".join(items) + " -1")
    return "\n".join(spmf_lines)

def _parse_spmf_sequence(content_str):
# spmf
    lines = content_str.strip().split("\n")
    if not lines:
        return None
    for line in lines:
        tokens = line.strip().split()
        if not tokens:
            return None
        if tokens[-1] != "-2":
            return None
    return content_str
