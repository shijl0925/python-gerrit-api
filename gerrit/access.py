#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from gerrit import GerritClient


class GerritAccess:
    def __init__(self, gerrit: GerritClient):
        self.gerrit = gerrit
        self.endpoint = "/access"

    def list(self, projects):
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

    def create_change(self, input_):
        """
        Creates a change to modify access rights for one or more projects.
        This endpoint is functionally equivalent to calling
        Create Access Rights Change per project, but handles multiple projects in a single request.

        .. code-block:: python

            input_ = {
                "project": "All-Projects",
                "subject": "Update access rights",
                "add": {
                    "refs/heads/*": {
                        "permissions": {
                            "read": {
                                "rules": {
                                    "global:Anonymous-Users": {
                                        "action": "ALLOW"
                                    }
                                }
                            }
                        }
                    }
                }
            }
            result = client.access.create_change(input_)

        :param input_: the ProjectAccessInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-access.html#project-access-input
        :return: ChangeInfo entity describing the resulting change
        """
        return self.gerrit.post(
            self.endpoint + "/", json=input_, headers=self.gerrit.default_headers
        )
