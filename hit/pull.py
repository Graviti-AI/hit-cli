#!/usr/bin/env python3
#
# Copyright 2022 Graviti. Licensed under MIT License.
#

"""Implementation of hit pull."""

import sys
from subprocess import CalledProcessError, run

from hit.utility import get_current_branch, update_main


def _implement_pull() -> None:
    try:
        branch = get_current_branch()
    except CalledProcessError:
        sys.exit(1)

    try:
        if branch != "main":
            run(["git", "checkout", "main"], check=True)

        update_main()

    except CalledProcessError:
        sys.exit(1)

    finally:
        if branch != "main":
            run(["git", "checkout", branch], check=True)
