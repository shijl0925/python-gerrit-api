#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi

from gerrit.utils.models import BaseModel


class GerritProjectLabel(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entity_name = "name"
        self.endpoint = f"/projects/{self.project}/labels/{self.name}"

    def set(self, input_):
        """
        Updates the definition of a label that is defined in this project.
        The calling user must have write access to the refs/meta/config branch of the project.
        Properties which are not set in the input entity are not modified.

        .. code-block:: python

            input_ = {
                "commit_message": "Ignore self approvals for Code-Review label",
                "ignore_self_approval": true
            }

            project = client.projects.get("MyProject")
            label = project.labels.get("foo")
            result = label.set(input_)

        :param input_: the LabelDefinitionInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-projects.html#label-definition-input
        :return:
        """
        result = self.gerrit.put(self.endpoint, json=input_, headers=self.gerrit.default_headers)
        return self.gerrit.projects.get(self.project).labels.get(result.get("name"))

    def delete(self):
        """
        Deletes the definition of a label that is defined in this project.
        The calling user must have write access to the refs/meta/config branch of the project.

        :return:
        """
        self.gerrit.delete(self.endpoint)


class GerritProjectLabels(object):
    def __init__(self, project, gerrit):
        self.project = project
        self.gerrit = gerrit
        self.endpoint = f"/projects/{self.project}/labels"

    def list(self):
        """
        Lists the labels that are defined in this project.

        :return:
        """
        result = self.gerrit.get(self.endpoint + "/")
        return GerritProjectLabel.parse_list(result, gerrit=self.gerrit)

    def get(self, name):
        """
        Retrieves the definition of a label that is defined in this project.
        The calling user must have read access to the refs/meta/config branch of the project.

        :param name: label name
        :return:
        """
        result = self.gerrit.get(self.endpoint + f"/{name}")
        return GerritProjectLabel(json=result, gerrit=self.gerrit)

    def create(self, name, input_):
        """
        Creates a new label definition in this project.
        The calling user must have write access to the refs/meta/config branch of the project.
        If a label with this name is already defined in this project, this label definition is
        updated (see Set Label).

        .. code-block:: python

            input_ = {
                "values": {
                    " 0": "No score",
                    "-1": "I would prefer this is not merged as is",
                    "-2": "This shall not be merged",
                    "+1": "Looks good to me, but someone else must approve",
                    "+2": "Looks good to me, approved"
                },
                "commit_message": "Create Foo Label"
            }
            new_label = project.labels.create('foo', input_)

        :param name: label name
        :param input_: the LabelDefinitionInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-projects.html#label-definition-input
        :return:
        """
        result = self.gerrit.put(
            self.endpoint + f"/{name}", json=input_, headers=self.gerrit.default_headers)
        return GerritProjectLabel(json=result, gerrit=self.gerrit)

    def delete(self, name):
        """
        Deletes the definition of a label that is defined in this project.
        The calling user must have write access to the refs/meta/config branch of the project.

        :param name: label name
        :return:
        """
        self.gerrit.delete(self.endpoint + f"/{name}")
