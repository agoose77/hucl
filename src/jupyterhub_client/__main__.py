# SPDX-FileCopyrightText: 2026-present Angus Hollands <goosey15@gmail.com>
#
# SPDX-License-Identifier: MIT
import sys

if __name__ == "__main__":
    from jupyterhub_client.cli import jupyterhub_client

    sys.exit(jupyterhub_client())
