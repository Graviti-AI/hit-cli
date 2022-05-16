#!/usr/bin/env python3
#
# Copyright 2022 Graviti. Licensed under MIT License.
#

"""Implementation of hit push."""


from hit.utility import clean_commit_message


def _implement_reword(file: str) -> None:
    with open(file, encoding="utf-8") as fp:
        lines = []
        for line in fp:
            if not line:
                break
            lines.append(line.replace("pick", "reword", 1))

    with open(file, "w", encoding="utf-8") as fp:
        fp.write("".join(lines))


def _implement_append(url: str, file: str) -> None:
    with open(file, encoding="utf-8") as fp:
        lines = clean_commit_message(fp)
        lines.append(url)

    with open(file, "w", encoding="utf-8") as fp:
        fp.write("\n".join(lines))
