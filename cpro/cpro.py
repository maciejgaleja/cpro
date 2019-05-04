import Context.Context
import logging


def main() -> None:
    ctx = Context.Context.Context('.')


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
