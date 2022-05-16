#!/usr/bin/env python3
#
# Copyright 2022 Graviti. Licensed under MIT License.
#

"""Implementation of hit clean."""

import sys
from subprocess import CalledProcessError
from typing import Optional

from hit.utility import clean_branch, fatal_and_kill, get_current_branch


def _implement_clean(branch: Optional[str], yes: bool) -> None:
    try:
        current_branch = get_current_branch()
        target_branch = branch if branch else current_branch
        if target_branch == "main":
            fatal_and_kill(f"Do not execute 'hit clean' on {target_branch} branch!")

        clean_branch(target_branch, yes, target_branch == current_branch)

    except CalledProcessError:
        sys.exit(1)
