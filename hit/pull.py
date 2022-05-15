#!/usr/bin/env python3
#
# Copyright (c) 2021 GRAVITI. All rights reserved.
# Contents cannot be copied or distributed without the permission of GRAVITI.
#

"""Implementation of hit pull."""

import sys
from subprocess import CalledProcessError, run

from .utility import get_current_branch, sync_everything


def _implement_pull() -> None:
    try:
        branch = get_current_branch()
    except CalledProcessError:
        sys.exit(1)

    try:
        if branch != "main":
            run(["git", "checkout", "main"], check=True)

        sync_everything()

    except CalledProcessError:
        sys.exit(1)

    finally:
        if branch != "main":
            run(["git", "checkout", branch], check=True)
