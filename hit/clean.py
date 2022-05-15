#!/usr/bin/env python3
#
# Copyright (c) 2021 GRAVITI. All rights reserved.
# Contents cannot be copied or distributed without the permission of GRAVITI.
#

"""Implementation of hit clean."""

import sys
from subprocess import CalledProcessError
from typing import Optional

from .utility import clean_branch, fatal, get_current_branch


def _implement_clean(branch: Optional[str], yes: bool) -> None:
    try:
        current_branch = get_current_branch()
        target_branch = branch if branch else current_branch
        if target_branch == "main":
            fatal(f"Do not execute 'hit clean' on {target_branch} branch!")

        clean_branch(target_branch, yes, target_branch == current_branch)

    except CalledProcessError:
        sys.exit(1)
