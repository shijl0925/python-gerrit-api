#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi

from gerrit.utils.models import BaseModel


class GerritProjectDashboard(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def delete(self):
        """
        Deletes a project dashboard.

        :return:
        """
        self.gerrit.delete(f"/projects/{self.project}/dashboards/{self.id}")


class GerritProjectDashboards(object):
    def __init__(self, project, gerrit):
        self.project = project
        self.gerrit = gerrit
        self.endpoint = f"/projects/{self.project}/dashboards"

    def list(self):
        """
        List custom dashboards for a project.

        :return:
        """
        result = self.gerrit.get(self.endpoint + "/")
        return GerritProjectDashboard.parse_list(result, project=self.project, gerrit=self.gerrit)

    def create(self, id_, input_):
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
          https://gerrit-review.googlesource.com/Documentation/rest-api-projects.html
          #dashboard-input
        :return:
        """
        result = self.gerrit.put(
            self.endpoint + f"/{id_}", json=input_, headers=self.gerrit.default_headers)
        return GerritProjectDashboard(json=result, project=self.project, gerrit=self.gerrit)

    def get(self, id_):
        """
        Retrieves a project dashboard. The dashboard can be defined on that project or be inherited
        from a parent project.

        :param id_: the dashboard id
        :return:
        """
        result = self.gerrit.get(self.endpoint + f"/{id_}")
        return GerritProjectDashboard(json=result, project=self.project, gerrit=self.gerrit)

    def delete(self, id_):
        """
        Deletes a project dashboard.

        :param id_: the dashboard id
        :return:
        """
        self.gerrit.delete(self.endpoint + f"/{id_}")
