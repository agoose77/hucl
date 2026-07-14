import argparse

from ..flows.shared import ensure_api_url
from ..flows.user_create import create_user
from ..drivers.sync import sync_driver


def setup_cli(parser: argparse.ArgumentParser):
    parser.add_argument("url", help="JupyterHub API URL")
    parser.add_argument("token", help="JupyterHub API Token")
    parser.add_argument("user", help="User name")
    parser.add_argument("--admin", action="store_true", help="Set admin flag on user")
    parser.set_defaults(impl=handle_args)
    return parser


def handle_args(args: argparse.Namespace):
    sync_driver(
        create_user(
            api_url=ensure_api_url(args.url),
            api_token=args.token,
            user_name=args.user,
            admin=args.admin,
        )
    )
