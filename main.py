from core import Builder


def main():
    builder = Builder(config_dir="config")
    builder.build()
    builder.save()


if __name__ == '__main__':
    main()
