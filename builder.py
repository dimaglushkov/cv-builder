import re

phrases_regex = re.compile("%.*%")

lists_regex = re.compile(";#.*;#", re.MULTILINE | re.DOTALL)
list_target_regex = re.compile(";#([a-zA-Z0-9_]*)")
list_elem_regex = re.compile(";#[a-zA-Z0-9_]*$(.*);#", re.MULTILINE | re.DOTALL)


def translate(text: str) -> str:
    for phrase in re.findall(phrases_regex, text):
        var_name_list = phrase[1:-1].split(".")
        for i in range(len(var_name_list)):
            var_name_list[i] = "[\"" + var_name_list[i] + "\"]"
        var_name = "".join(var_name_list)
        text = text.replace(phrase, "%" + var_name + "%")
    return text


def build(text: str, data: dict) -> str:
    text = translate(text)
    for list_ in re.findall(lists_regex, text):
        list_target = re.findall(list_target_regex, list_)[0]
        list_size = len(data[list_target])
        list_elem = re.findall(list_elem_regex, list_)[0]
        list_val = ""
        for i in range(list_size):
            list_val += insert_phrases(list_elem, data[list_target][i])
        text = text.replace(list_, list_val)

    text = insert_phrases(text, data)
    return text


def insert_phrases(text: str, data: dict) -> str:
    for phrase in re.findall(phrases_regex, text):
        key = phrase[1:-1]
        text = text.replace(phrase, eval(f"data{key}"))

    return text
