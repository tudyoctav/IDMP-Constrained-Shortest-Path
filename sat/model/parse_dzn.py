import re

list_detect_regex = re.compile(r"(?<=\[).*(?=\])")
list_split_regex = re.compile(r"\s*,\s*")

def get_par(inp: str, par: str, typ = int):
    regex = re.compile(par + r"\s*=\s*(?P<val>.*)\s*;")
    res = regex.search(inp).group("val")
    list_res = list_detect_regex.search(res)
    if list_res:
        vals_str = list_res.group(0)
        print(vals_str)
        value_list = list_split_regex.split(vals_str)
        return list(map(typ, value_list))
    return typ(res)