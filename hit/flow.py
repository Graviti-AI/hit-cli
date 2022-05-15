#!/usr/bin/env python3
#
# Copyright 2022 Graviti. Licensed under MIT License.
#

"""Graviti Github workflow CLI."""

from subprocess import PIPE, Popen, run
from typing import List, Tuple

import click

from .utility import fatal, get_current_branch, warning

REVERT_MESSAGE = """REVERT: revert {} commits for new release

This reverts commits:
{}
"""


@click.group()
def flow() -> None:
    """Revert flow command group.\f"""  # noqa: D415, D301


@flow.command()
@click.argument("tag", type=str)
def release(tag: str) -> None:
    """Release current branch with given tag for revert flow.\f

    Arguments:
        tag: the given tag

    """  # noqa: D415, D301
    release_branch = get_current_branch()
    if release_branch == "main":
        fatal(f"Do not hit release in {release_branch} branch!")

    run(["git", "checkout", "main"], check=True)

    revert_commit, start_commit = _get_fork_commit("main", release_branch)

    # revert phase
    revert_range = f"{revert_commit}.."
    reverts = _list_commits(revert_range)
    revert_number = len(reverts)
    if revert_number:
        run(["git", "revert", "--no-commit", revert_range], check=True)

        message = REVERT_MESSAGE.format(revert_number, "\n".join(reverts))
        run(["git", "commit", "--message", message], check=True)
    else:
        fast_forward_commit, start_commit = _get_fast_forward_commit(release_branch, start_commit)
        run(["git", "merge", "--ff-only", fast_forward_commit], check=True)

    # cherry-pick phase
    cherry_pick_range = f"{start_commit}..{release_branch}"
    if len(_list_commits(cherry_pick_range)):
        run(["git", "cherry-pick", "--ff", cherry_pick_range], check=True)

    # release phase
    run(["git", "tag", tag], check=True)

    # cheanup phase
    run(["git", "branch", "-D", release_branch], check=True)


@flow.command()
@click.argument("branch_name", type=str)
@click.option("-d", "--delete", is_flag=True)
@click.option("--init", is_flag=True)
def branch(branch_name: str, delete: bool, init: bool) -> None:
    """Create new develop branch for revert flow.\f

    Arguments:
        branch_name: the name of the new created branch.
        delete: delete branch and related tags
        init: set init flag "True" when creating the first "revert flow" branch

    """  # noqa: D415, D301
    if delete:
        run(["git", "branch", "-D", branch_name], check=True)
        return

    if init:
        source_branch = "main"
    else:
        source_branch = get_current_branch()
        if source_branch == "main":
            fatal(f"Do not hit branch in {source_branch} branch!")

    revert_commit, start_commit = _get_fork_commit("main", source_branch)
    run(["git", "checkout", "-b", branch_name, revert_commit], check=True)
    if not init:
        cherry_pick_range = f"{start_commit}..{source_branch}"
        if len(_list_commits(cherry_pick_range)):
            run(["git", "cherry-pick", "--ff", cherry_pick_range], check=True)
        else:
            warning("No commit to create new branch")


def _is_diff_empty(commit: str) -> bool:
    result = run(["git", "diff", commit], check=True, stdout=PIPE)
    return not bool(result.stdout)


def _get_merge_base(base: str, head: str) -> str:
    result = run(["git", "merge-base", base, head], check=True, stdout=PIPE)
    return result.stdout.decode().strip()


def _get_patch_id(commit: str) -> str:
    result = run(["git", "show", commit], check=True, stdout=PIPE)

    process = Popen(["git", "patch-id"], stdin=PIPE, stdout=PIPE)
    stdout = process.communicate(result.stdout)[0]
    return stdout.decode().split()[0]


def _get_overlap(base: List[str], head: List[str]) -> Tuple[int, str, str]:
    overlap_length = 1
    overlap_end_base = base[0]
    overlap_end_head = head[0]

    for base_commit, head_commit in zip(base[1:], head[1:]):
        if _get_patch_id(base_commit) != _get_patch_id(head_commit):
            break

        overlap_length += 1
        overlap_end_base = base_commit
        overlap_end_head = head_commit

    return overlap_length, overlap_end_base, overlap_end_head


def _get_fork_commit(base: str, head: str) -> Tuple[str, str]:
    fork_base = fork_head = _get_merge_base(base, head)

    base_commits = _list_commits(f"{fork_base}..{base}", True)
    head_commits = _list_commits(f"{fork_head}..{head}", True)

    if not base_commits or not head_commits:
        return fork_base, fork_head

    head_start_patch_id = _get_patch_id(head_commits[0])

    candidates = []
    for base_commit in base_commits:
        if _get_patch_id(base_commit) == head_start_patch_id and _is_diff_empty(
            f"{fork_base}..{base_commit}^"
        ):
            candidates.append(base_commit)

    max_overlap_length = 0
    for candidate in candidates:
        index = base_commits.index(candidate)
        overlap_length, base_commit, head_commit = _get_overlap(base_commits[index:], head_commits)

        if overlap_length >= max_overlap_length:
            max_overlap_length = overlap_length
            fork_base = base_commit
            fork_head = head_commit

    return fork_base, fork_head


def _get_fast_forward_commit(release_branch: str, start_commit: str) -> Tuple[str, str]:
    other_branches = set(_get_branches_contains("main")) - {"main"}
    if release_branch in other_branches:
        return release_branch, release_branch

    max_overlap_length = 0
    fast_forward_commit = "main"
    new_start_commit = start_commit

    release_commits = _list_commits(f"{start_commit}^..{release_branch}", True)

    for other_branch in other_branches:
        other_commits = _list_commits(f"main^..{other_branch}", True)

        overlap_length, fast_forward_commit_candidate, start_commit_candidate = _get_overlap(
            other_commits, release_commits
        )

        if overlap_length >= max_overlap_length:
            max_overlap_length = overlap_length
            fast_forward_commit = fast_forward_commit_candidate
            new_start_commit = start_commit_candidate

    return fast_forward_commit, new_start_commit


def _get_branches_contains(commit: str) -> List[str]:
    result = run(
        ["git", "branch", "--format=%(refname:short)", "--contains", commit],
        check=True,
        stdout=PIPE,
    )
    return result.stdout.decode().strip().split()


def _list_commits(commits: str, reverse: bool = False) -> List[str]:
    command = ["git", "log", commits, "--format=%H"]
    if reverse:
        command += ["--reverse"]
    result = run(command, check=True, stdout=PIPE)
    return result.stdout.decode().strip().split()
