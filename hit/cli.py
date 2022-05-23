#!/usr/bin/env python3
#
# Copyright 2022 Graviti. Licensed under MIT License.
#
# pylint: disable=import-outside-toplevel

"""Graviti Github workflow CLI."""

from typing import Optional

import click

from hit import __version__


@click.group(context_settings={"help_option_names": ("-h", "--help")})
@click.version_option(__version__)
def hit() -> None:
    """Usage: 'hit' + COMMAND.\f"""  # noqa: D415, D301


@hit.command()
@click.option("-p", "--phabricator", is_flag=True, help="Auth for Phabricator.")
def auth(phabricator: bool) -> None:
    """Get Github Auth for hit CLI.\f

    Arguments:
        phabricator: Whether auth with Phabricator.

    """  # noqa: D415, D301
    from hit.auth import _implement_auth

    _implement_auth(phabricator)


@hit.command()
@click.argument("repository", type=str)
@click.argument("directory", type=str, required=False)
def clone(repository: str, directory: Optional[str]) -> None:
    """Fork + clone + initialize the target github repo for hit CLI.\f

    Arguments:
        repository: The repository name needs to be forked and cloned
        directory: The newly created directory the repo needs to be cloned to

    """  # noqa: D415, D301
    from hit.clone import _implement_clone

    _implement_clone(repository, directory)


@hit.command()
def pull() -> None:
    """Sync the local and remote develop repo with upstream repo.\f"""  # noqa: D415, D301
    from hit.pull import _implement_pull

    _implement_pull()


@hit.command()
@click.option("-f", "--force", is_flag=True, help="Whether to git push with -f.")
def push(force: bool) -> None:
    """Push the local branch to remote and create/update the pull request.\f

    Arguments:
        force: Whether to git push with -f.

    """  # noqa: D415, D301
    from hit.push import _implement_push

    _implement_push(force)


@hit.command()
@click.option("-y", "--yes", is_flag=True, help="Run non-interactively with 'yes' to all prompts.")
def land(yes: bool) -> None:
    """Merge the pull request then clean and sync repo.\f

    Arguments:
        yes: Run non-interactively with 'yes' to all prompts.

    """  # noqa: D415, D301
    from hit.land import _implement_land

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
    from hit.clean import _implement_clean

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
    from hit.message import _implement_reword

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
    from hit.message import _implement_append

    _implement_append(url, file)


if __name__ == "__main__":
    hit()
