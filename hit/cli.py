#!/usr/bin/env python3
#
# Copyright 2022 Graviti. Licensed under MIT License.
#
# pylint: disable=import-outside-toplevel

"""Graviti Github workflow CLI."""

from typing import Optional

import click

from . import __version__


@click.group()
@click.version_option(__version__)
def hit() -> None:
    """Usage: 'hit' + COMMAND.\f"""  # noqa: D415, D301


@hit.command()
def auth() -> None:
    """Get Github Auth for hit CLI.\f"""  # noqa: D415, D301
    from .auth import _implement_auth

    _implement_auth()


@hit.command()
@click.argument("repository", type=str)
@click.argument("directory", type=str, required=False)
def clone(repository: str, directory: Optional[str]) -> None:
    """Fork then clone the target github repo for hit CLI.\f

    Arguments:
        repository: The repository name needs to be forked and cloned
        directory: The newly created directory the repo needs to be cloned to

    """  # noqa: D415, D301
    from .clone import _implement_clone

    _implement_clone(repository, directory)


@hit.command()
def pull() -> None:
    """Sync the local and remote develop repo with upstream repo.\f"""  # noqa: D415, D301
    from .pull import _implement_pull

    _implement_pull()


@hit.command()
@click.option("-f", "--force", is_flag=True, help="Whether to git push with -f.")
@click.option("-y", "--yes", is_flag=True, help="Run non-interactively with 'yes' to all prompts.")
def push(force: bool, yes: bool) -> None:
    """Push the local branch to remote and create/update the pull request.\f

    Arguments:
        force: Whether to git push with -f.
        yes: Run non-interactively with 'yes' to all prompts.

    """  # noqa: D415, D301
    from .push import _implement_push

    _implement_push(force, yes)


@hit.command()
@click.option("-y", "--yes", is_flag=True, help="Run non-interactively with 'yes' to all prompts.")
def land(yes: bool) -> None:
    """Merge the pull request then clean and sync repo.\f

    Arguments:
        yes: Run non-interactively with 'yes' to all prompts.

    """  # noqa: D415, D301
    from .land import _implement_land

    _implement_land(yes)


@hit.command()
@click.argument("branch", type=str, required=False)
@click.option("-y", "--yes", is_flag=True, help="Run non-interactively with 'yes' to all prompts.")
def clean(branch: Optional[str], yes: bool) -> None:
    """Detele useless local and remote develop branch.\f

    Arguments:
        branch: The branch name needs to be deleted
        yes: Run non-interactively with 'yes' to all prompts.

    """  # noqa: D415, D301
    from .clean import _implement_clean

    _implement_clean(branch, yes)


@hit.group(hidden=True)
def message() -> None:
    """Git message modifier.\f"""  # noqa: D415, D301


@message.command()
@click.argument("file", type=str)
def reword(file: str) -> None:
    """Git sequence editor to change pick to reword in rebase file.\f

    Arguments:
        file: The git rebase interactive file name.

    """  # noqa: D415, D301
    from .message import _implement_reword

    _implement_reword(file)


@message.command()
@click.argument("url", type=str)
@click.argument("file", type=str)
def append(url: str, file: str) -> None:
    """Git editor to append the pull request url to the commit message.\f

    Arguments:
        url: The pull request needs to be appended to the commit message.
        file: The git commit message file name.

    """  # noqa: D415, D301
    from .message import _implement_append

    _implement_append(url, file)


if __name__ == "__main__":
    hit()
