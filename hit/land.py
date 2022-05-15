#!/usr/bin/env python3
#
# Copyright 2022 Graviti. Licensed under MIT License.
#

"""Implementation of hit land."""

import os
import sys
from subprocess import PIPE, CalledProcessError, run
from time import sleep

import click
from github import Commit, Github, GithubException

from .utility import (
    PR_CLOSED,
    clean_branch,
    fatal,
    get_current_branch,
    get_upstream_repo_name,
    read_config,
    sync_everything,
    warning,
)


def _implement_land(yes: bool) -> None:
    try:
        branch = get_current_branch()
        if branch == "main":
            fatal(f"Do not execute 'hit land' on {branch} branch!")

        token = read_config()["github"]["token"]
        github = Github(token)

        repo = github.get_repo(get_upstream_repo_name())

        head = f"{github.get_user().login}:{branch}"
        pulls = repo.get_pulls(head=head)
        pulls_count = pulls.totalCount
        if pulls_count == 0:
            fatal("No pull request found for this branch!")
        elif pulls_count == 1:
            pull_request = pulls[0]
            url = pull_request.html_url

            commit_count = pull_request.commits
            if commit_count > 1:
                warning("Pull request contains more than 1 commit.")
                if not yes:
                    click.confirm("Do you want to continue?", abort=True)
                    click.echo()

            remote_commits = pull_request.get_commits()
            remote_head = remote_commits[commit_count - 1]
            _check_pull_request_sha(remote_head)
            _check_pull_request_checks(remote_head, yes)

            _append_pull_request_url(f"{remote_commits[0].sha}^", url)

            try:
                sleep(1)
                pull_request.merge(merge_method="rebase", sha=_get_head_sha())
            except GithubException as error:
                if error.status in (405, 409):
                    if error.status == 409:
                        warning(f"{error.data['message']} Run 'hit land' again may fix it.")
                    else:
                        fatal(error.data["message"], kill=False)  # type: ignore[arg-type]

                    click.secho(url, underline=True)
                    sys.exit(1)

                raise
        else:
            fatal("This branch is linked to more than one pull requests!")

        click.secho("> Pull Requset Merged:", fg="green")
        click.secho(url, underline=True)

        click.secho("\n> Cleaning:", bold=True)
        clean_branch(branch, True, True)
        click.secho("\n> Updating:", bold=True)
        sync_everything()

    except CalledProcessError:
        sys.exit(1)


def _get_head_sha() -> str:
    result = run(["git", "log", "--format=%H", "-n1"], stdout=PIPE, check=True)
    return result.stdout.decode().strip()


def _check_pull_request_sha(commit: Commit.Commit) -> None:
    local_commit_sha = _get_head_sha()
    if local_commit_sha != commit.sha:
        fatal("Unpushed changes detected, please push it before landing!")


def _check_pull_request_checks(commit: Commit.Commit, yes: bool) -> None:
    completed_flag = True
    success_flag = True

    for suite in commit.get_check_suites():  # type: ignore[call-arg]
        if suite.status != "completed":
            completed_flag = False
        elif suite.conclusion != "success":
            success_flag = False
            break

    if not success_flag:
        fatal("Not all Checks have passed!", False)
    elif not completed_flag:
        warning("Not all Checks have finished!")
    else:
        return

    if not yes:
        click.confirm("Do you want to continue?", abort=True)
    click.echo()


def _append_pull_request_url(base: str, url: str) -> None:
    result = run(["git", "log", "--format=%H", f"{base}.."], stdout=PIPE, check=True)
    commits = result.stdout.decode().strip().split("\n")

    trailer = f"{PR_CLOSED}{url}"

    for commit in commits:
        result = run(["git", "log", "--format=%b", "-n1", commit], stdout=PIPE, check=True)
        lines = result.stdout.decode().strip().split("\n")

        match = False
        for line in reversed(lines):
            if not line:
                continue

            if not match:
                if line == trailer:
                    match = True
                    continue

                break

            if line.startswith(PR_CLOSED):
                match = False
                break

        if not match:
            break

    else:
        return

    env = os.environ.copy()
    env["GIT_EDITOR"] = f"hit message append '{trailer}'"
    env["GIT_SEQUENCE_EDITOR"] = "hit message reword"

    click.secho("> Rewording:", bold=True)
    click.echo("Appending pull request URL to commit message.")
    run(["git", "rebase", "--interactive", "--quiet", base], env=env, stdout=PIPE, check=True)

    click.secho("\n> Pushing:", bold=True)
    run(["git", "push", "--force"], check=True)
    click.echo()
