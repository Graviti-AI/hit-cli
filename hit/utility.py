#!/usr/bin/env python3
#
# Copyright 2022 Graviti. Licensed under MIT License.
#

"""Graviti hit CLI utility functions."""

import os
import sys
from configparser import ConfigParser
from subprocess import PIPE, run
from typing import Iterable, List, Optional

import click

PR_CLOSED = "PR Closed: "


def config_filepath() -> str:
    """Get path of the config file.

    Returns:
        The path of config file.

    """
    home = "USERPROFILE" if os.name == "nt" else "HOME"
    return os.path.join(os.environ[home], ".hitconfig")


def read_config() -> ConfigParser:
    """Get config parser of the config file.

    Returns:
        The ConfigParser object of config file.

    """
    config_file = config_filepath()
    if not os.path.exists(config_file):
        fatal("Config file does not exist!")

    config_parser = ConfigParser()
    config_parser.read(config_file)
    return config_parser


def get_current_branch() -> str:
    """Get the name of current branch.

    Returns:
        The name of current branch

    """
    result = run(["git", "branch", "--show-current"], check=True, stdout=PIPE)
    return result.stdout.decode().strip()


def get_remote_branch(branch: str = "") -> Optional[str]:
    """Get the name of remote branch.

    Arguments:
        branch: The name of the local branch

    Returns:
        The name of remote branch, return None if it does not exist.

    """
    upstream_command = ["git", "rev-parse", "--abbrev-ref", f"{branch}@{{u}}"]
    result = run(upstream_command, check=False, stdout=PIPE, stderr=PIPE)
    if result.returncode != 0:
        return None

    return result.stdout.decode().strip()


def get_upstream_repo_name() -> str:
    """Get the name of upstream repo.

    Returns:
        The name of upstream repo.

    """
    result = run(["git", "remote", "get-url", "upstream"], stdout=PIPE, check=True)
    ssh_url = result.stdout.decode().strip()
    if not ssh_url.startswith("git@github.com:") or not ssh_url.endswith(".git"):
        fatal("Upstream url '{ssh_url}' is not a github SSH key!")

    return ssh_url[15:-4]


def clean_branch(branch: str, yes: bool, main: bool) -> None:
    """Delete current branch and its upstream branch.

    Arguments:
        branch: Targat branch name.
        yes: Run non-interactively with 'yes' to all prompts.
        main: Whteher to checkout to "main" before cleaning.

    """
    run(["git", "fetch", "--prune"], check=True)

    remote_branch = get_remote_branch(branch)

    if not yes:
        if remote_branch:
            message = (
                f"Local branch '{branch}' and "
                f"remote branch '{remote_branch}' will be completely deleted."
            )
        else:
            message = (
                f"Remote branch not found.\nLocal branch '{branch}' will be completely deleted."
            )
        click.secho(message, fg="yellow")
        click.confirm("Do you want to continue?", abort=True)

    if main:
        run(["git", "checkout", "main"], check=True)
    run(["git", "branch", "-D", branch], check=True)
    if remote_branch:
        run(["git", "push", "--prune", "--delete"] + remote_branch.split("/", 1), check=True)


def clean_commit_message(lines: Iterable[str]) -> List[str]:
    """Chean the commit message.

    Arguments:
        lines: The commite messsage lines.

    Returns:
        The commit message lines after cleaning.

    """
    results = []
    is_blank = True
    for line in lines:
        line = line.rstrip()
        if line.startswith("#"):
            continue

        if not line or line.startswith(PR_CLOSED):
            if not is_blank:
                is_blank = True
                results.append("")
            continue

        is_blank = False
        results.append(line)

    if not is_blank:
        results.append("")

    return results


def sync_everything() -> None:
    """Pull latest code from upstream, and push it to origin."""
    run(["git", "pull", "upstream", "main", "--ff-only", "--no-rebase"], check=True)
    run(["git", "push"], check=True)


def fatal(message: str, kill: bool = True) -> None:
    """Print the message in FATAL style then exit the program with code 1.

    Arguments:
        message: The fatal message.
        kill: whether to exit the program.

    """
    click.secho(f"FATAL: {message}", err=True, fg="red")
    if kill:
        sys.exit(1)


def warning(message: str) -> None:
    """Print the message in WARNING style then exit the program with code 1.

    Arguments:
        message: The warning message.

    """
    click.secho(f"WARNING: {message}", err=True, fg="yellow")
