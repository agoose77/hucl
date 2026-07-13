import argparse
import logging

from ..flows.shared import ensure_api_url
from ..flows.start import start_server_sansio
from ..drivers.sync import sync_driver


def setup_cli(parser: argparse.ArgumentParser):
    parser.add_argument("url", help="JupyterHub API URL")
    parser.add_argument("token", help="JupyterHub API Token")
    parser.add_argument("--user", help="User name", default=None)
    parser.add_argument("--server", help="Server name")
    parser.add_argument(
        "--profile-option",
        help="Profile option key-value pair of the form key=value",
        nargs="*",
        action="extend",
        default=[],
    )
    parser.set_defaults(impl=handle_args)
    return parser


def handle_args(args: argparse.Namespace):
    # Arg processing
    profile_options = {k: v for k, v in (p.split("=") for p in args.profile_option)}

    server_url = sync_driver(
        start_server_sansio(
            api_url=ensure_api_url(args.url),
            api_token=args.token,
            user_name=args.user,
            server_name=args.server,
            profile_options=profile_options,
        )
    )
    print(repr(server_url))
