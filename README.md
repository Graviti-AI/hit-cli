# Github Workflow CLI —— hit

The github pull request based workflow is quite tedious and complicated,
`hit` CLI simplify the workflow by wrapping `git` CLI and github API.

## Installation

`hit` CLI has below dependences:

-   [`git`](https://git-scm.com)

Install `hit` CLI by pip:

```bash
pip3 install hit-cli
```

## Usage

```bash
$ hit --help
Usage: hit [OPTIONS] COMMAND [ARGS]...

  Usage: 'hit' + COMMAND.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  auth   Get Github Auth for hit CLI.
  clean  Detele useless local and remote develop branch.
  clone  Fork then clone the target github repo for hit CLI.
  land   Merge the pull request then clean and sync repo.
  pull   Sync the local and remote develop repo with upstream repo.
  push   Push the local branch to remote and create/update the pull request.
```

## Shell completion

```bash
# add this to your ~/.bashrc
eval "$(_HIT_COMPLETE=source_bash hit)"
```

```zsh
# add this to your ~/.zshrc
eval "$(_HIT_COMPLETE=source_zsh hit)"
```

```fish
# add this to your ~/.config/fish/completions/foo-bar.fish
eval (env _HIT_COMPLETE=source_fish hit)
```

See detailed info in [Click Shell Completion](https://click.palletsprojects.com/en/7.x/bashcomplete/)
