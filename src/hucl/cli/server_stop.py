import argparse

from ..flows.shared import ensure_api_url
from ..flows.server_stop import stop_server
from ..drivers.sync import sync_driver


def setup_cli(parser: argparse.ArgumentParser):
    parser.add_argument("url", help="JupyterHub API URL")
    parser.add_argument("token", help="JupyterHub API Token")
    parser.add_argument("--user", help="User name", default=None)
    parser.add_argument("--server", help="Server name")
    parser.add_argument(
        "-v", "--verbose", help="Turn on verbose debugging", action="store_true"
    )
    parser.add_argument(
        "--remove",
        help="Delete the server once it has stopped",
        action="store_true",
    )
    parser.set_defaults(impl=handle_args)
    return parser


def handle_args(args: argparse.Namespace):
    sync_driver(
        stop_server(
            api_url=ensure_api_url(args.url),
            api_token=args.token,
            user_name=args.user,
            server_name=args.server,
            remove=args.remove,
        )
    )
