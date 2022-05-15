# Github Workflow CLI —— fit

The github pull request based workflow is quite tedious and complicated,
`fit` CLI simplify the workflow by wrapping `git` CLI and github API.

## Installation

`fit` CLI has below dependences:

-   [`git`](https://git-scm.com)

Install `fit` CLI by pip:

```
lang=bash
pip3 install fit-cli
```

## Usage

```
lang=bash
$ fit --help
Usage: fit [OPTIONS] COMMAND [ARGS]...

  Usage: 'fit' + COMMAND.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  auth   Get Github Auth for fit CLI.
  clean  Detele useless local and remote develop branch.
  clone  Fork then clone the target github repo for fit CLI.
  land   Merge the pull request then clean and sync repo.
  pull   Sync the local and remote develop repo with upstream repo.
  push   Push the local branch to remote and create/update the pull request.
```

## Shell completion

```
lang=bash, name=bash
# add this to your ~/.bashrc
eval "$(_FIT_COMPLETE=source_bash fit)"
```

```
lang=zsh, name=zsh
# add this to your ~/.zshrc
eval "$(_FIT_COMPLETE=source_zsh fit)"
```

```
lang=fish, name=fish
# add this to your ~/.config/fish/completions/foo-bar.fish
eval (env _FIT_COMPLETE=source_fish fit)
```

See detailed info in [Click Shell Completion](https://click.palletsprojects.com/en/7.x/bashcomplete/)
