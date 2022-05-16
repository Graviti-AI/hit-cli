#!/usr/bin/env python3
#
# Copyright 2022 Graviti. Licensed under MIT License.
#

"""Implementation of hit clone."""

import os
import sys
from subprocess import CalledProcessError, run
from typing import Optional

import click
from github import Github
from github.GithubException import UnknownObjectException

from hit.utility import fatal_and_kill, read_config


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

    directory = directory if directory else repository.split("/", 1)[1]
    try:
        run(["git", "clone", forked_repo.ssh_url, directory], check=True)
        os.chdir(directory)
        run(["git", "remote", "add", "upstream", origin_repo.ssh_url], check=True)
        run(["git", "config", "--local", "remote.upstream.gh-resolved", "base"], check=True)
    except CalledProcessError:
        sys.exit(1)


def _get_repo_name(repository: str) -> str:
    if repository.startswith("https://github.com/"):
        return "/".join(repository[19:].split("/", 2)[:2])

    if repository.startswith("git@github.com") and repository.endswith(".git"):
        return repository[15:-4]

    return repository
