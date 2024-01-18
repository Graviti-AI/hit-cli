#!/usr/bin/env python3
#
# Copyright 2022 Graviti. Licensed under MIT License.
#

"""Implementation of hit pull."""

import sys
from subprocess import CalledProcessError, run

from hit.utility import ENV, get_base_branch, get_current_branch, update_branch


def _implement_pull() -> None:
    try:
        branch = get_current_branch()
        base = get_base_branch()
    except CalledProcessError:
        sys.exit(1)

    try:
        if branch != base:
            run(["git", "checkout", base], env=ENV, check=True)

        update_branch(base)

    except CalledProcessError:
        sys.exit(1)

    finally:
        if branch != base:
            run(["git", "checkout", branch], env=ENV, check=True)
