import Context
import Operations
import logging
import os


def main() -> None:
    ctx = Context.Context('tests/header-guard')
    filename = os.path.join(ctx.path, 'src/FileIterator.hpp')
    oper = Operations.HeaderComment(ctx, filename, filename)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
