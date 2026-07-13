# SPDX-FileCopyrightText: 2026-present Angus Hollands <goosey15@gmail.com>
#
# SPDX-License-Identifier: MIT
import argparse
import logging
import os

from .server_start import setup_cli as add_start
from .server_stop import setup_cli as add_stop

from .user_create import setup_cli as add_create_user
from .user_delete import setup_cli as add_delete_user


def main(argv: list[str] = None):
    logging.basicConfig(
        filename="hucl.log",
        level=os.environ.get("JUPYTERHUB_CLIENT_LOGLEVEL", "INFO"),
    )

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    server = subparsers.add_parser("server")
    server_parsers = server.add_subparsers(required=True)

    add_start(server_parsers.add_parser("start"))
    add_stop(server_parsers.add_parser("stop"))

    user = subparsers.add_parser("user")
    user_parsers = user.add_subparsers(required=True)

    add_create_user(user_parsers.add_parser("create"))
    add_delete_user(user_parsers.add_parser("delete"))

    args = parser.parse_args()
    args.impl(args)


if __name__ == "__main__":
    main()
