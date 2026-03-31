#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from typing import Any
from gerrit import GerritClient
from gerrit.utils.gerritbase import GerritBase


class GerritProjectDashboard(GerritBase):
    def __init__(self, id: str, project: str, gerrit: GerritClient) -> None:
        self.id = id
        self.project = project
        self.gerrit = gerrit
        self.endpoint = f"/projects/{self.project}/dashboards/{self.id}"
        super().__init__()

    def __str__(self) -> str:
        return str(self.id)

    def set(self, input_: Any) -> Any:
        """
        Updates a project dashboard.

        .. code-block:: python

            input_ = {
                "id": "master:closed",
                "commit_message": "Update the default dashboard"
            }
            dashboard = project.dashboards.get('master:closed')
            result = dashboard.set(input_)

        :param input_: the DashboardInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-projects.html#dashboard-input
        :return:
        """
        return self.gerrit.put(
            self.endpoint, json=input_, headers=self.gerrit.default_headers
        )

    def delete(self) -> None:
        """
        Deletes a project dashboard.

        :return:
        """
        self.gerrit.delete(self.endpoint)


class GerritProjectDashboards:
    def __init__(self, project: str, gerrit: GerritClient) -> None:
        self.project = project
        self.gerrit = gerrit
        self.endpoint = f"/projects/{self.project}/dashboards"

    def list(self) -> Any:
        """
        List custom dashboards for a project.

        :return:
        """
        result = self.gerrit.get(self.endpoint + "/")
        return result

    def create(self, id_: str, input_: Any) -> Any:
        """
        Creates a project dashboard, if a project dashboard with the given dashboard ID doesn't
        exist yet.

        .. code-block:: python

            input_ = {
                "id": "master:closed",
                "commit_message": "Define the default dashboard"
            }
            new_dashboard = project.dashboards.create('master:closed', input_)


        :param id_: the dashboard id
        :param input_: the DashboardInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-projects.html#dashboard-input
        :return:
        """
        result = self.gerrit.put(
            self.endpoint + f"/{id_}", json=input_, headers=self.gerrit.default_headers
        )
        return result

    def get(self, id_: str) -> Any:
        """
        Retrieves a project dashboard. The dashboard can be defined on that project or be inherited
        from a parent project.

        :param id_: the dashboard id
        :return:
        """
        result = self.gerrit.get(self.endpoint + f"/{id_}")

        dashboard_id = result.get("id")
        return GerritProjectDashboard(
            id=dashboard_id, project=self.project, gerrit=self.gerrit
        )

    def delete(self, id_: str) -> None:
        """
        Deletes a project dashboard.

        :param id_: the dashboard id
        :return:
        """
        self.gerrit.delete(self.endpoint + f"/{id_}")
