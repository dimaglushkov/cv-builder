import os

import yaml
import sys

from builder import builder


def load_templates(config: dict) -> list:
    templates = []
    theme_dir = f"themes/{config['app']['theme']}"
    theme_files = os.listdir(theme_dir)
    template_files = [i for i in theme_files if i.endswith(".html")]
    for template_file in template_files:
        with open(theme_dir + "/" + template_file) as file:
            text = file.read()
            templates.append(text)
    return templates


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


def main():
    config = dict()
    with open("config/config.yml") as config_file:
        try:
            config = yaml.safe_load(config_file)
        except yaml.YAMLError as exc:
            print(exc, file=sys.stderr)
            exit(1)

    data = load_data(config)
    templates = load_templates(config)
    generated = dict()
    for lang in config["app"]["languages"]:
        generated[lang] = list()
        for template in templates:
            generated[lang].append(builder.build(template, data[lang]))
    print(generated["en"][0])


if __name__ == '__main__':
    main()
