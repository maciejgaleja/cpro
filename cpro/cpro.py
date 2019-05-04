import Context
import Operations
import logging
import os


def main() -> None:
    ctx = Context.Context('tests/header-guard')
    filename = os.path.join(ctx.path, 'src/FileIterator.hpp')
    oper = Operations.HeaderComment(ctx, filename)
    oper.run()

    operInc = Operations.PreIncludes(ctx, filename)
    operInc.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
