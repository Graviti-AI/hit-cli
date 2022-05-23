#!/usr/bin/env python3
#
# Copyright 2022 Graviti. Licensed under MIT License.
#

"""Implementation of hit clone."""

import os
import sys
from subprocess import CalledProcessError, run
from typing import Any, Dict, List, Optional

import click
from github import Github
from github.GithubException import UnknownObjectException

from hit.utility import fatal_and_kill, read_config

_PRECOMMIT_CONFIG_PATH = ".pre-commit-config.yaml"


def _implement_clone(repository: str, directory: Optional[str]) -> None:
    token = read_config()["github"]["token"]
    github = Github(token)
    name = _get_repo_name(repository)
    try:
        origin_repo = github.get_repo(name)
    except UnknownObjectException:
        fatal_and_kill(f"Repository '{name}' not found!")

    forked_repo = origin_repo.create_fork()

    click.echo(f"> Forked repository: {click.style(forked_repo.full_name, bold=True)}\n")

    directory = directory if directory else name.split("/", 1)[1]
    try:
        run(["git", "clone", forked_repo.ssh_url, directory], check=True)
        os.chdir(directory)
        run(["git", "remote", "add", "upstream", origin_repo.ssh_url], check=True)
        run(["git", "config", "--local", "remote.upstream.gh-resolved", "base"], check=True)
    except CalledProcessError:
        sys.exit(1)

    _install_precommit_scripts()


def _get_repo_name(repository: str) -> str:
    if repository.startswith("https://github.com/"):
        return "/".join(repository[19:].split("/", 2)[:2])

    if repository.startswith("git@github.com") and repository.endswith(".git"):
        return repository[15:-4]

    return repository


def _install_precommit_scripts() -> None:
    if not os.path.exists(_PRECOMMIT_CONFIG_PATH):
        return

    click.echo("\n> Installing 'pre-commit' scripts:\n")

    try:
        # pylint: disable=import-outside-toplevel
        from pre_commit.clientlib import load_config
        from pre_commit.commands.install_uninstall import install
        from pre_commit.store import Store
    except ModuleNotFoundError:
        click.echo(
            f"'{_PRECOMMIT_CONFIG_PATH}' is found in the repo, but 'pre-commit' is not installed.\n"
            "Skip the 'pre-commit' scripts installation phrase.\n"
            "\n"
            "To install 'pre-commit', run:\n"
            "  pip install pre-commit\n"
            "\n"
            "To install the 'pre-commit' scripts for the repo, run:\n"
            "  pre-commit install [-t {hook types}]\n"
            "\n"
            "Check 'https://pre-commit.com/index.html' for more info."
        )
        return

    config: Dict[str, Any] = load_config(_PRECOMMIT_CONFIG_PATH)

    stages: List[str] = config.get("default_stages", [])
    for repo in config["repos"]:
        for hook in repo["hooks"]:
            stages.extend(hook.get("stages", []))

    install(_PRECOMMIT_CONFIG_PATH, Store(), stages)
