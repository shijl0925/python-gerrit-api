#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from typing import Any
from gerrit import GerritClient
from gerrit.utils.gerritbase import GerritBase


class GerritProjectSubmitRequirement(GerritBase):
    def __init__(self, name: str, project: str, gerrit: GerritClient) -> None:
        self.name = name
        self.project = project
        self.gerrit = gerrit
        self.endpoint = f"/projects/{self.project}/submit_requirements/{self.name}"
        super().__init__()

    def __str__(self) -> str:
        return self.name

    def update(self, input_) -> Any:
        """
        Updates a submit requirement for a project.
        The calling user must have write access to the refs/meta/config branch of the project.

        .. code-block:: python

            input_ = {
                "submittability_expression": "label:Code-Review=MAX AND label:Verified=MAX",
                "allow_override_in_child_projects": True
            }
            sr = project.submit_requirements.get("Code-Review")
            result = sr.update(input_)

        :param input_: the SubmitRequirementInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-projects.html#submit-requirement-input
        :return:
        """
        return self.gerrit.post(
            self.endpoint, json=input_, headers=self.gerrit.default_headers
        )

    def delete(self) -> None:
        """
        Deletes a submit requirement from a project.
        The calling user must have write access to the refs/meta/config branch of the project.

        :return:
        """
        self.gerrit.delete(self.endpoint)


class GerritProjectSubmitRequirements:
    def __init__(self, project: str, gerrit: GerritClient) -> None:
        self.project = project
        self.gerrit = gerrit
        self.endpoint = f"/projects/{self.project}/submit_requirements"

    def list(self) -> Any:
        """
        Lists the submit requirements for a project.

        :return: list of SubmitRequirementInfo entities,
          https://gerrit-review.googlesource.com/Documentation/rest-api-projects.html#submit-requirement-info
        """
        return self.gerrit.get(self.endpoint + "/")

    def get(self, name) -> Any:
        """
        Retrieves a submit requirement of a project.

        :param name: the submit requirement name
        :return:
        """
        result = self.gerrit.get(self.endpoint + f"/{name}")
        sr_name = result.get("name")
        return GerritProjectSubmitRequirement(
            name=sr_name, project=self.project, gerrit=self.gerrit
        )

    def create(self, name, input_) -> Any:
        """
        Creates a new submit requirement for a project.
        The calling user must have write access to the refs/meta/config branch of the project.

        .. code-block:: python

            input_ = {
                "submittability_expression": "label:Code-Review=MAX,user=non_uploader",
                "description": "Requires a Code-Review vote from a non-uploader",
                "allow_override_in_child_projects": True
            }
            new_sr = project.submit_requirements.create("Code-Review", input_)

        :param name: the submit requirement name
        :param input_: the SubmitRequirementInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-projects.html#submit-requirement-input
        :return:
        """
        result = self.gerrit.put(
            self.endpoint + f"/{name}", json=input_, headers=self.gerrit.default_headers
        )
        return result

    def delete(self, name) -> None:
        """
        Deletes a submit requirement from a project.
        The calling user must have write access to the refs/meta/config branch of the project.

        :param name: the submit requirement name
        :return:
        """
        self.gerrit.delete(self.endpoint + f"/{name}")
