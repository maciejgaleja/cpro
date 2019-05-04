import Context
import File
import logging


def main() -> None:
    ctx = Context.Context('.')
    ctx.git(['--version'])
    file = File.File('./cpro/cpro.py', ctx)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
