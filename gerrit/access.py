#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from typing import Any, List
from gerrit import GerritClient


class GerritAccess:
    def __init__(self, gerrit: GerritClient) -> None:
        self.gerrit = gerrit
        self.endpoint = "/access"

    def list(self, projects: List[str]) -> Any:
        """
        Lists the access rights for projects.
        As result a map is returned that maps the project name to the ProjectAccessInfo entity.

        .. code-block:: python

            result = client.access.list(projects=["All-Projects", "myproject"])

        :param projects: list of project names to limit the results to
        :return: map of project name to ProjectAccessInfo entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-access.html#project-access-info
        """
        params = [("project", p) for p in projects]
        return self.gerrit.get(self.endpoint + "/", params=params)
