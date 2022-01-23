import os
import re
import shutil
import sys

import yaml


class Builder:
    def __init__(self, config_dir="config"):
        self.attr_regex = re.compile("%[a-zA-Z0-9._]*%")

        self.cond_attr_regex = re.compile("\?[^\?]*\?", re.MULTILINE | re.DOTALL)
        self.cond_attr_target_regex = re.compile("\?([a-zA-Z0-9_.]*)")
        self.cond_attr_elem_regex = re.compile("\?[a-zA-Z0-9_.]*(.*)\?", re.MULTILINE | re.DOTALL)

        self.lists_regex = re.compile(";#[^;#]*;#", re.MULTILINE | re.DOTALL)
        self.list_target_regex = re.compile(";#([a-zA-Z0-9_.]*)")
        self.list_elem_regex = re.compile(";#[a-zA-Z0-9_.]*$(.*);#", re.MULTILINE | re.DOTALL)

        self.config_dir = config_dir
        self.config = dict()
        self.data = None
        self.templates = None
        self.results = None
        self.cur_lang = None
        with open(os.path.join(self.config_dir, "config.yml")) as config_file:
            try:
                self.config = yaml.safe_load(config_file)
            except yaml.YAMLError as exc:
                print(exc, file=sys.stderr)
                exit(1)

        self.data = self.__load_data()
        self.templates = self.__load_templates()

    def build(self):
        self.results = dict()
        for lang in self.config["app"]["languages"]:
            self.results[lang] = dict()
            self.cur_lang = lang
            for name, text in self.templates.items():
                self.results[lang][name] = self.__generate_file(text)

    def save(self):
        if os.path.exists(self.config["app"]["output"]):
            shutil.rmtree(self.config["app"]["output"])

        theme_dir_path = os.path.join("themes", self.config["app"]["theme"])
        os.mkdir(self.config["app"]["output"])
        theme_dirs = [d for d in os.listdir(theme_dir_path) if os.path.isdir(os.path.join(theme_dir_path, d))]
        for theme_dir in theme_dirs:
            shutil.copytree(os.path.join(theme_dir_path, theme_dir), os.path.join(self.config["app"]["output"], theme_dir))
        shutil.copytree("assets", os.path.join(self.config["app"]["output"], "assets"))

        for lang, page in self.results.items():
            prefix = f"{lang}_"
            if lang == self.config["app"]["languages"][0]:
                prefix = ""
            for name, page_text in page.items():
                with open(os.path.join(self.config["app"]["output"], prefix + name), "w") as file:
                    file.write(page_text)

    def __generate_file(self, text: str) -> str:
        for list_attr in re.findall(self.lists_regex, text):
            list_target = re.findall(self.list_target_regex, list_attr)[0]
            ctx = list_target.split(".") if "." in list_target else [list_target]
            list_size = len(self.__get_attr_val(ctx))
            list_elem = re.findall(self.list_elem_regex, list_attr)[0]
            list_attr_val = ""
            for i in range(list_size):
                list_attr_val += self.__insert_attr_val(list_elem, ctx=ctx + [i])

            text = text.replace(list_attr, list_attr_val)
        text = self.__insert_attr_val(text)
        return text

    def __insert_attr_val(self, text: str, ctx=None) -> str:
        if ctx is None:
            ctx = list()
        for conditional_attr in re.findall(self.cond_attr_regex, text):
            target = re.findall(self.cond_attr_target_regex, conditional_attr)[0].split(".")
            target = target if isinstance(target, list) else [target]

            elem = re.findall(self.cond_attr_elem_regex, conditional_attr)[0]
            if self.__check_conditional_attr(ctx + target):
                elem_value = self.__insert_attr_val(elem, ctx=ctx)
                text = text.replace(conditional_attr, elem_value)
            else:
                text = text.replace(conditional_attr, "")

        for attr in re.findall(self.attr_regex, text):
            target = attr[1:-1].split(".")
            target = target if isinstance(target, list) else [target]
            text = text.replace(attr, self.__get_attr_val(ctx + target))
        return text

    def __check_conditional_attr(self, attr_keys: list) -> bool:
        depth = len(attr_keys)
        val = self.data[self.cur_lang][attr_keys[0]]
        for i in range(1, depth):
            if isinstance(val, list) and len(val) > int(attr_keys[i]):
                val = val[int(attr_keys[i])]
            elif isinstance(val, dict) and attr_keys[i] in val.keys():
                val = val[attr_keys[i]]
            else:
                return False
        return True

    def __get_attr_val(self, attr_keys: list):
        depth = len(attr_keys)
        val = self.data[self.cur_lang][attr_keys[0]]
        for i in range(1, depth):
            try:
                key = int(attr_keys[i]) if isinstance(val, list) else attr_keys[i]
                val = val[key]
            except (NameError, KeyError, TypeError) as err:
                attr_keys = [str(key) for key in attr_keys]
                print(f"Exception occurred while getting {'.'.join(attr_keys)} from {self.cur_lang}.yml: {err}", file=sys.stderr)
                exit(1)
        return val

    def __load_data(self) -> dict:
        data = dict()
        for lang in self.config["app"]["languages"]:
            with open(os.path.join(self.config_dir, f"{lang}.yml")) as data_file:
                try:
                    data[lang] = yaml.safe_load(data_file)
                except yaml.YAMLError as exc:
                    print(exc, file=sys.stderr)
                    exit(1)
        return data

    def __load_templates(self) -> dict:
        templates = dict()
        theme_dir = os.path.join("themes", self.config['app']['theme'])
        if not os.path.exists(theme_dir):
            print(f"{theme_dir} does not exist")
            exit(1)
        theme_files = os.listdir(theme_dir)
        template_names = [i for i in theme_files if i.endswith(".html")]
        for template_name in template_names:
            with open(os.path.join(theme_dir, template_name)) as template_file:
                text = template_file.read()
                templates[template_name] = text
        return templates

