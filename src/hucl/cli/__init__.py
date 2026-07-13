# SPDX-FileCopyrightText: 2026-present Angus Hollands <goosey15@gmail.com>
#
# SPDX-License-Identifier: MIT
import argparse
import logging
import os

from .start import setup_cli as add_start
from .stop import setup_cli as add_stop


def main(argv: list[str] = None):
    logging.basicConfig(
        filename="hucl.log",
        level=os.environ.get("JUPYTERHUB_CLIENT_LOGLEVEL", "INFO"),
    )

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)
    add_start(subparsers.add_parser("start"))
    add_stop(subparsers.add_parser("stop"))
    args = parser.parse_args()
    args.impl(args)


if __name__ == "__main__":
    main()
