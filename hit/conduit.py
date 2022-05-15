#!/usr/bin/env python3
#
# Copyright 2022 Graviti. Licensed under MIT License.
#

"""Phabricator Conduit Client."""

from typing import Any, Dict, Optional
from urllib.parse import urljoin

from requests import Session

_REMARKUP_MARKER = "> ## {icon github} Pull Requests:"


class ConduitError(Exception):
    """The phabricator conduit exception class.

    Arguments:
        response: The response of conduit request.

    """

    def __init__(self, response: Dict[str, str]):
        super().__init__()
        self.code = response["error_code"]
        self.info = response["error_info"]

    def __str__(self) -> str:
        return f"{self.code}: {self.info}"


class Conduit:
    """The phabricator conduit client class.

    Arguments:
        url: Phabricator URL.
        token: Phabricator API token.

    """

    def __init__(self, url: str, token: str) -> None:
        self._url = urljoin(url, "api/")
        self._token = token
        self._session = Session()

    def _post(self, section: str, post_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = urljoin(self._url, section)

        if not post_data:
            post_data = {}

        post_data["api.token"] = self._token
        response = self._session.post(url=url, data=post_data).json()
        result = response["result"]
        if not result:
            raise ConduitError(response)

        return result  # type: ignore[no-any-return]

    @staticmethod
    def _insert_url(description: str, url: str) -> Optional[str]:
        lines = description.split("\n")
        insert_url = f"> {url}"
        try:
            index = lines.index(_REMARKUP_MARKER) + 1
        except ValueError:
            lines.append(_REMARKUP_MARKER)
            lines.append(insert_url)
        else:
            for i, line in enumerate(lines[index:], index):
                if not line.startswith("> "):
                    break

                if line == insert_url:
                    return None

            lines.insert(i + 1, insert_url)  # pylint: disable=undefined-loop-variable

        return "\n".join(lines)

    def get_user(self) -> str:
        """Get the phabricator user name.

        Returns:
            The phabricator user name.

        """
        return self._post("user.whoami")["userName"]  # type: ignore[no-any-return]

    def get_description(self, task: int) -> str:
        """Get the phabricator task description.

        Arguments:
            task: The target task number.

        Returns:
            The description of the task.

        Raises:
            ConduitError: When the task does not exists.

        """
        post_data = {"constraints[ids][0]": task}
        result = self._post("maniphest.search", post_data)
        data = result["data"]
        if len(data) == 0:
            raise ConduitError(
                {"error_code": "Task-Not-Found", "error_info": f"Task 'T{task}' does not exists"}
            )

        return data[0]["fields"]["description"]["raw"]  # type: ignore[no-any-return]

    def append_to_description(self, task: int, url: str) -> None:
        """Append the pull request url to the specific task.

        Arguments:
            task: The target task number.
            url: The pull request url to append.

        """
        description = self._insert_url(self.get_description(task), url)
        if not description:
            return

        post_data = {
            "objectIdentifier": str(task),
            "transactions[0][type]": "description",
            "transactions[0][value]": description,
        }
        self._post("maniphest.edit", post_data)
