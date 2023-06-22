import math
from pathlib import Path
import pandas as pd


def concat_graph(x) -> str :
    result = x["generation method"]
    if result == 'open maps':
        result = x["city"] + f"({x['city size']})"
    else:
        if x['N'] is None:
            result = result + f"(" + x["problem"] + ")"
        else:
            assert x["N"] != -1
            result = result + f"_" + str(x["N"]).zfill(2)
    return result

def format_float(f: float, float_format:str, nan_format=str):
    if math.isnan(f):
        return nan_format
    else:
        return float_format.format(f)

def get_table_str(sub_row: str, df: pd.DataFrame, float_format=" ${:2.2f}$", nan_format="$>60.00$") -> str:
    df = df.sort_values(["graph", "algorithm", "weight generation", sub_row])
    algorithms = df["algorithm"].unique()
    weight_generation = df["weight generation"].unique()
    window_generation = df[sub_row].unique()
    graphs = df["graph"].unique()
    n_collumns = len(algorithms) * len(weight_generation) * len(window_generation) + 1
    result = f"\\begin{{tabular}}{{{'l'* n_collumns}}}\n"
    result += "\\toprule\n"
    headers = [["graph "],
               ["      "],
               ["      "]]
    for alg in algorithms:
        headers[0].append((f"\\multicolumn{{4}}{{c}}{{{alg}}}"))
        for wg in weight_generation:
            headers[1].append(f"\\multicolumn{{2}}{{c}}{{{wg}}}")
            for win_g in window_generation:
                headers[2].append(f"{win_g}")
    if len(algorithms) == 1:
        del headers[0]
        headers[0][0] = "graph "
    headers = map(" & ".join, headers)

    rows = []
    for graph in graphs:
        solve_times = list(df.loc[df["graph"] == graph, "solve_time"])
        row = [graph] + list(map(lambda f: format_float(f, float_format, nan_format), solve_times))
        rows.append(" & ".join(row))
    result += " \\\\\n".join(headers)
    result += "\\\\\n\\midrule\n"
    result += " \\\\\n".join(rows)
    result += "\\\\\n\\bottomrule"
    result += "\n\\end{tabular}"
    result = result.replace("_", "\\_")
    return result

COLLUMN_FORMAT = {"graph": "graph", "algorithm": {"weight generation": {"window generation": "solve_time"}}}
def rcsp_report(df: pd.DataFrame, out_file: str):
    out_file = Path(out_file)
    df["graph"] = df.apply(concat_graph, 1)

    df = df[["graph", "algorithm", "weight generation", "window generation", "solve_time"]]
    with open(out_file, "w") as f:
        print(get_table_str("window generation", df), file=f)    

def ncsp_report(df: pd.DataFrame, out_file: str):
    out_file = Path(out_file)
    df["graph"] = df.apply(concat_graph, 1)

    df = df[["graph", "algorithm", "weight generation", "penalty generation", "solve_time", "run_dir"]]
    with open(out_file, "w") as f:
        print(get_table_str("penalty generation", df), file=f)    
    
def tcsp_report(df: pd.DataFrame, out_file: str):
    out_file = Path(out_file)
    df["graph"] = df.apply(concat_graph, 1)

    df = df[["graph", "algorithm", "weight generation", "task generation", "solve_time"]]
    with open(out_file, "w") as f:
        print(get_table_str("task generation", df), file=f)  