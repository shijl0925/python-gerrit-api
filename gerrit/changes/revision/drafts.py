#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi

from gerrit.utils.models import BaseModel


class GerritChangeRevisionDraft(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.endpoint = f"/changes/{self.change}/revisions/{self.revision}/drafts/{self.id}"

    def update(self, input_):
        """
        Updates a draft comment on a revision.

        .. code-block:: python

            input_ = {
                "path": "sonarqube/cloud/duplications.py",
                "line": 25,
                "message": "[nit] trailing whitespace"
            }
            change = client.changes.get('Project~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            revision = change.get_revision('3848807f587dbd3a7e61723bbfbf1ad13ad5a00a')
            draft = revision.drafts.get('89f04e8c_9b7fd51d')
            result = draft.update(input_)

        :param input_: the CommentInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#comment-input
        :return:
        """
        result = self.gerrit.put(self.endpoint, json=input_, headers=self.gerrit.default_headers)
        return GerritChangeRevisionDraft.parse(
            result, change=self.change, revision=self.revision, gerrit=self.gerrit
        )

    def delete(self):
        """
        Deletes a draft comment from a revision.

        :return:
        """
        self.gerrit.delete(self.endpoint)


class GerritChangeRevisionDrafts(object):
    def __init__(self, change, revision, gerrit):
        self.change = change
        self.revision = revision
        self.gerrit = gerrit
        self.endpoint = self.gerrit.get(f"/changes/{self.change}/revisions/{self.revision}/drafts")

    def list(self):
        """
        Lists the draft comments of a revision that belong to the calling user.

        :return:
        """
        result = self.gerrit.get(f"/changes/{self.change}/revisions/{self.revision}/drafts")
        drafts = []
        for key, value in result.items():
            for item in value:
                draft = item
                draft.update({"path": key})
                drafts.append(draft)
        return GerritChangeRevisionDraft.parse_list(
            drafts, change=self.change, revision=self.revision, gerrit=self.gerrit
        )

    def get(self, id_):
        """
        Retrieves a draft comment of a revision that belongs to the calling user.

        :param id_: the draft comment id
        :return:
        """
        result = self.gerrit.get(self.endpoint + f"/{id_}")
        return GerritChangeRevisionDraft.parse(
            result, change=self.change, revision=self.revision, gerrit=self.gerrit
        )

    def create(self, input_):
        """
        Creates a draft comment on a revision.

        .. code-block:: python

            input_ = {
                "path": "sonarqube/cloud/duplications.py",
                "line": 15,
                "message": "[nit] trailing whitespace"
            }
            change = client.changes.get('Project~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            revision = change.get_revision('3848807f587dbd3a7e61723bbfbf1ad13ad5a00a')
            new_draft = revision.drafts.create(input_)

        :param input_: the CommentInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#comment-input
        :return:
        """
        result = self.gerrit.put(self.endpoint, json=input_, headers=self.gerrit.default_headers)
        return GerritChangeRevisionDraft.parse(
            result, change=self.change, revision=self.revision, gerrit=self.gerrit
        )

    def delete(self, id_):
        """
        Deletes a draft comment from a revision.

        :param id_: the draft comment id
        :return:
        """
        self.gerrit.delete(self.endpoint + f"/{id_}")
