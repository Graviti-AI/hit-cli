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

from .utility import fatal, read_config


def _implement_clone(repository: str, directory: Optional[str]) -> None:
    token = read_config()["github"]["token"]
    github = Github(token)
    try:
        origin_repo = github.get_repo(repository)
    except UnknownObjectException:
        fatal(f"Repository '{repository}' not found!")

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
