#!/usr/bin/env python3
#
# Copyright 2022 Graviti. Licensed under MIT License.
#

"""Implementation of hit auth."""

from configparser import ConfigParser

import click
from github import Github
from github.GithubException import BadCredentialsException

from hit.utility import config_filepath, fatal_and_kill


def _implement_auth() -> None:
    config_parser = ConfigParser()
    config_file = config_filepath()
    config_parser.read(config_file)

    github_token = _auth_for_github()

    config_parser.add_section("github")
    config_parser["github"]["token"] = github_token

    with open(config_file, "w", encoding="utf-8") as fp:
        config_parser.write(fp)

    success = click.style("Success!", fg="green")
    click.echo(f"\n> {success} the information has been written to '{config_file}'.")


def _auth_for_github() -> str:
    click.echo("=" * 80)
    click.secho("Github Auth:", fg="green")
    url = click.style("https://github.com/settings/tokens", underline=True)
    click.echo(f"\n> Visit {url} to generate your Personal Access Token.")
    click.echo("> The minimum required scopes are 'repo' and 'read:org'.")
    github_token = click.prompt("\nPaste your Github Access Token here")

    github = Github(github_token)
    user = github.get_user()
    try:
        name = user.login
        company = user.company
    except BadCredentialsException:
        fatal_and_kill("Invalid Github Token!")

    welcome_message = click.style(name if not company else f"{name} from {company}", bold=True)

    click.echo(f"\n> Github auth as {welcome_message}.\n")

    return github_token  # type: ignore[no-any-return]
