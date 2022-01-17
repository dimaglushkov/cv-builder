import os
import yaml
import sys
import shutil

import core


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


def main():
    cfg = dict()
    with open("config/config.yml") as config_file:
        try:
            cfg = yaml.safe_load(config_file)
        except yaml.YAMLError as exc:
            print(exc, file=sys.stderr)
            exit(1)

    data = load_data(cfg)
    templates = load_templates(cfg)

    pages = dict()
    for lang in cfg["app"]["languages"]:
        pages[lang] = dict()
        for name, text in templates.items():
            pages[lang][name] = core.build(text, data[lang])

    save_results(pages, cfg)


if __name__ == '__main__':
    main()
