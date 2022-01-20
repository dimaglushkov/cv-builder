import os
import re
import shutil
import sys

import yaml


class Builder:
    def __init__(self, config_dir="config"):
        self.attr_regex = re.compile("%[a-zA-Z0-9_\[\]\"\-\.]*%")
        self.lists_regex = re.compile(";#[^;#]*;#", re.MULTILINE | re.DOTALL)
        self.list_target_regex = re.compile(";#([a-zA-Z0-9_]*)")
        self.list_elem_regex = re.compile(";#[a-zA-Z0-9_]*$(.*);#", re.MULTILINE | re.DOTALL)

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

    def get_results(self) -> dict:
        return self.results

    def __generate_file(self, text: str) -> str:
        # TODO: implement support for sublists like ;#general.contacts
        for list_attr in re.findall(self.lists_regex, text):
            list_target = re.findall(self.list_target_regex, list_attr)[0]
            ctx = [list_target]
            list_size = len(self.data[self.cur_lang][list_target])
            list_elem = re.findall(self.list_elem_regex, list_attr)[0]
            list_attr_val = ""
            for i in range(list_size):
                list_attr_val += self.__insert_attr_value(list_elem, ctx=ctx + [i])
            text = text.replace(list_attr, list_attr_val)
        text = self.__insert_attr_value(text)
        return text

    def __insert_attr_value(self, text: str, ctx=None) -> str:
        if ctx is None:
            ctx = list()
        for attr in re.findall(self.attr_regex, text):
            key = attr[1:-1].split(".")
            key = key if isinstance(key, list) else [key]
            text = text.replace(attr, self.__get_attr_val(ctx + key))
        return text

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

    def __get_attr_val(self, attr_keys: list) -> str:
        if len(attr_keys) == 1:
            if attr_keys in self.data[self.cur_lang].keys():
                return self.data[self.cur_lang][attr_keys]
            else:
                print(f"Can't find attr \"{attr_keys}\" at {self.cur_lang}.yml", file=sys.stderr)
                exit(1)

        depth = len(attr_keys)
        val = self.data[self.cur_lang][attr_keys[0]]
        for i in range(1, depth):
            try:
                key = int(attr_keys[i]) if isinstance(val, list) else attr_keys[i]
                val = val[key]
            except (NameError, KeyError, TypeError) as err:
                print(f"Exception occurred while getting {'.'.join(attr_keys)} from {self.cur_lang}.yml: {err}", file=sys.stderr)
                exit(1)
        return val
