#!/usr/bin/env python3
#
# Copyright 2022 Graviti. Licensed under MIT License.
#

"""Implementation of hit push."""

import sys
from subprocess import PIPE, CalledProcessError, run
from typing import Tuple

import click
from github import Github, GithubException, PullRequest, Repository

from hit.utility import (
    ENV,
    clean_commit_message,
    fatal,
    fatal_and_kill,
    get_current_branch,
    get_remote_branch,
    get_repo_names,
    read_config,
    warning,
)


def _implement_push(force: bool) -> None:
    try:
        branch = get_current_branch()
        if branch == "main":
            fatal_and_kill(f"Do not execute 'hit push' on {branch} branch!")

        config = read_config()
        github = Github(config["github"]["token"])

        origin_name, upstream_name = get_repo_names()

        repo = github.get_repo(upstream_name)

        head = f"{origin_name}:{branch}"
        pulls = repo.get_pulls(head=head)

        pulls_count = pulls.totalCount
        if pulls_count == 0:
            _git_push(branch, force)
            pull_request = _create_pull_request(repo, f"{origin_name.split('/', 1)[0]}:{branch}")

            click.secho("\n> Pull Requset Created:", fg="green")
        elif pulls_count == 1:
            _git_push(branch, force)
            pull_request = pulls[0]
            _update_pull_request(pull_request)

            click.secho("\n> Pull Requset Updated:", fg="green")
        else:
            fatal_and_kill("This branch is linked to more than one pull requests!")

        click.secho(pull_request.html_url, underline=True)

        if pull_request.commits > 1:
            click.echo()
            warning("Pull request contains more than 1 commit.")

    except CalledProcessError:
        sys.exit(1)


def _git_push(branch: str, force: bool) -> None:
    click.secho("> Pushing:", bold=True)

    remote_branch = get_remote_branch()
    push_command = ["git", "push"]
    if not remote_branch:
        push_command += ("--set-upstream", "origin", branch)
    elif force:
        push_command.append("-f")

    run(push_command, env=ENV, check=True)


def _get_cleanup_commit_message() -> Tuple[str, str]:
    result = run(["git", "log", "--format=%B", "-n1"], env=ENV, stdout=PIPE, check=True)
    lines = result.stdout.decode().strip().split("\n")
    lines = clean_commit_message(lines)
    return lines[0], "\n".join(lines[1:]).strip()


def _create_pull_request(repo: Repository.Repository, head: str) -> PullRequest.PullRequest:
    title, body = _get_cleanup_commit_message()

    try:
        return repo.create_pull(title=title, body=body, base=repo.default_branch, head=head)
    except GithubException as error:
        if error.status == 422:
            for data in error.data["errors"]:
                fatal(data["message"])  # type: ignore[index]

            sys.exit(1)

        raise


def _update_pull_request(pull_request: PullRequest.PullRequest) -> None:
    title, body = _get_cleanup_commit_message()

    if pull_request.title == title and pull_request.body == (body if body else None):
        return

    pull_request.edit(title=title, body=body)
    click.echo("\n> Update Pull Requset Message:")
    click.secho(f"\n    {title}", bold=True)
    if body:
        click.echo()
        for line in body.split("\n"):
            click.echo(f"    {line}")
