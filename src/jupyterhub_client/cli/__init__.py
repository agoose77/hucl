# SPDX-FileCopyrightText: 2026-present Angus Hollands <goosey15@gmail.com>
#
# SPDX-License-Identifier: MIT
import argparse
import logging
import os

from .start import setup_cli


def main(argv: list[str] = None):
    logging.basicConfig(
        filename="jupyterhub-client.log",
        level=os.environ.get("JUPYTERHUB_CLIENT_LOGLEVEL", "INFO"),
    )

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)
    setup_cli(subparsers.add_parser("start"))
    args = parser.parse_args()
    args.impl(args)


if __name__ == "__main__":
    main()
