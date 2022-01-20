import yaml
import sys

import core


def main():
    cfg = dict()
    with open("config/config.yml") as config_file:
        try:
            cfg = yaml.safe_load(config_file)
        except yaml.YAMLError as exc:
            print(exc, file=sys.stderr)
            exit(1)

    data = core.load_data(cfg)
    templates = core.load_templates(cfg)

    pages = dict()
    for lang in cfg["app"]["languages"]:
        pages[lang] = dict()
        for name, text in templates.items():
            pages[lang][name] = core.build(text, data[lang], core.Context(lang=lang))

    core.save_results(pages, cfg)


if __name__ == '__main__':
    main()
