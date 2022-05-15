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

from .conduit import Conduit
from .utility import (
    clean_commit_message,
    fatal,
    get_current_branch,
    get_remote_branch,
    get_upstream_repo_name,
    read_config,
    warning,
)


def _implement_push(force: bool, yes: bool) -> None:
    try:
        branch = get_current_branch()
        if branch == "main":
            fatal(f"Do not execute 'hit push' on {branch} branch!")

        config = read_config()
        github = Github(config["github"]["token"])

        repo = github.get_repo(get_upstream_repo_name())

        head = f"{github.get_user().login}:{branch}"
        pulls = repo.get_pulls(head=head)

        pulls_count = pulls.totalCount
        if pulls_count == 0:
            task = _get_task_number(branch, yes)

            _git_push(branch, force)
            pull_request = _create_pull_request(repo, head)

            if task:
                conduit = Conduit(config["phabricator"]["url"], config["phabricator"]["token"])
                conduit.append_to_description(task, pull_request.html_url)
                click.secho("\n> Phabricator Task Linked:", fg="green")
                click.secho(f"{config['phabricator']['url']}T{task}", underline=True)

            click.secho("\n> Pull Requset Created:", fg="green")
        elif pulls_count == 1:
            _git_push(branch, force)
            pull_request = pulls[0]
            _update_pull_request(pull_request)

            click.secho("\n> Pull Requset Updated:", fg="green")
        else:
            fatal("This branch is linked to more than one pull requests!")

        click.secho(pull_request.html_url, underline=True)

        if pull_request.commits > 1:
            click.echo()
            warning("Pull request contains more than 1 commit.")

    except CalledProcessError:
        sys.exit(1)


def _get_task_number(branch: str, yes: bool) -> int:
    try:
        if not branch.startswith("T"):
            raise ValueError("The branch name does not start with 'T'")

        index = branch.find("_")
        task = branch[1:index] if index != -1 else branch[1:]

        return int(task)

    except ValueError:
        warning("Current branch name does not start with a phabricator task")
        if not yes:
            click.confirm("Do you want to continue?", abort=True)
        click.echo()
        return 0


def _git_push(branch: str, force: bool) -> None:
    click.secho("> Pushing:", bold=True)

    remote_branch = get_remote_branch()
    push_command = ["git", "push"]
    if not remote_branch:
        push_command += ("--set-upstream", "origin", branch)
    elif force:
        push_command.append("-f")

    run(push_command, check=True)


def _get_cleanup_commit_message() -> Tuple[str, str]:
    result = run(["git", "log", "--format=%B", "-n1"], stdout=PIPE, check=True)
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
                fatal(data["message"], kill=False)  # type: ignore[index]

            sys.exit(1)

        raise


def _update_pull_request(pull_request: PullRequest.PullRequest) -> None:
    title, body = _get_cleanup_commit_message()

    if pull_request.title == title and pull_request.body == body:
        return

    pull_request.edit(title=title, body=body)
    click.echo("\n> Update Pull Requset Message:")
    click.secho(f"\n    {title}", bold=True)
    if body:
        click.echo()
        for line in body.split("\n"):
            click.echo(f"    {line}")
