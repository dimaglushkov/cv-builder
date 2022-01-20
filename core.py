import os
import re
import shutil
import sys

import yaml

phrases_regex = re.compile("%[a-zA-Z0-9_\[\]\"\-\.]*%")

lists_regex = re.compile(";#.*;#", re.MULTILINE | re.DOTALL)
list_target_regex = re.compile(";#([a-zA-Z0-9_]*)")
list_elem_regex = re.compile(";#[a-zA-Z0-9_]*$(.*);#", re.MULTILINE | re.DOTALL)


class Context:
    def __init__(self, lang=None, obj=None):
        self.lang = lang
        self.obj = obj

    def desc(self) -> str:
        return f"file: {self.lang}.yml, list-object: {self.obj}" if self.obj is not None else f"file: {self.lang}.yml"


def load_data(config: dict) -> dict:
    data = dict()
    for lang in config["app"]["languages"]:
        with open(f"config/{lang}.yml") as data_file:
            try:
                data[lang] = yaml.safe_load(data_file)
            except yaml.YAMLError as exc:
                print(exc, file=sys.stderr)
                exit(1)
    return data


def load_templates(config: dict) -> dict:
    templates = dict()
    theme_dir = f"themes/{config['app']['theme']}"
    theme_files = os.listdir(theme_dir)
    template_names = [i for i in theme_files if i.endswith(".html")]
    for template_name in template_names:
        with open(os.path.join(theme_dir, template_name)) as template_file:
            text = template_file.read()
            templates[template_name] = text
    return templates


def save_results(pages: dict, cfg: dict) -> None:
    if os.path.exists(cfg["app"]["output"]):
        shutil.rmtree(cfg["app"]["output"])

    theme_dir_path = os.path.join("themes", cfg["app"]["theme"])
    os.mkdir(cfg["app"]["output"])
    theme_dirs = [d for d in os.listdir(theme_dir_path) if os.path.isdir(os.path.join(theme_dir_path, d))]
    for theme_dir in theme_dirs:
        shutil.copytree(os.path.join(theme_dir_path, theme_dir), os.path.join(cfg["app"]["output"], theme_dir))
    shutil.copytree("assets", os.path.join(cfg["app"]["output"], "assets"))

    for lang, page in pages.items():
        # use first language as default
        prefix = f"{lang}_"
        if lang == cfg["app"]["languages"][0]:
            prefix = ""
        for name, page_text in page.items():
            with open(os.path.join(cfg["app"]["output"], prefix + name), "w") as file:
                file.write(page_text)


def translate(text: str, data:dict) -> str:
    for phrase in re.findall(phrases_regex, text):
        var_name_list = phrase[1:-1].split(".")
        for i in range(len(var_name_list)):
            var_name_list[i] = "[\"" + var_name_list[i] + "\"]"
        var_name = "".join(var_name_list)
        valid = False
        text = text.replace(phrase, "%" + var_name + "%")
    return text


def build(text: str, data: dict, ctx: Context) -> str:
    text = translate(text, data)
    for list_ in re.findall(lists_regex, text):
        list_target = re.findall(list_target_regex, list_)[0]
        list_size = len(data[list_target])
        list_elem = re.findall(list_elem_regex, list_)[0]
        list_val = ""
        for i in range(list_size):
            list_val += insert_phrases(list_elem, data[list_target][i], Context(lang=ctx.lang, obj=list_target))
        text = text.replace(list_, list_val)

    text = insert_phrases(text, data, ctx)
    return text


def insert_phrases(text: str, data: dict, ctx: Context) -> str:
    for phrase in re.findall(phrases_regex, text):
        key = phrase[1:-1]
        try:
            text = text.replace(phrase, eval(f"data{key}"))
        except (NameError, KeyError):
            print(f"Error missing {key} parameter in {ctx.desc()}", file=sys.stderr)
            exit(1)
        except TypeError:
            print(f"None value for {key} field in {ctx.desc()}", file=sys.stderr)
            exit(1)

    return text
