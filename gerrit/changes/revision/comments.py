#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi

from gerrit.utils.models import BaseModel


class GerritChangeRevisionComment(BaseModel):
    def __init__(self, **kwargs):
        super(GerritChangeRevisionComment, self).__init__(**kwargs)

    def delete(self, input_=None):
        """
        Deletes a published comment of a revision. Instead of deleting the whole comment, this endpoint just replaces
        the comment’s message with a new message, which contains the name of the user who deletes the comment and the
        reason why it’s deleted.

        .. code-block:: python

            input_ = {
                "reason": "contains confidential information"
            }

            change = client.changes.get('myProject~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            revision = change.get_revision('3848807f587dbd3a7e61723bbfbf1ad13ad5a00a')
            comment = revision.comments.get("e167e775_e069567a")
            result = comment.delete(input_)
            # or
            result = comment.delete()

        :param input_: the DeleteCommentInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#delete-comment-input
        :return:
        """
        endpoint = f"/changes/{self.change}/revisions/{self.revision}/comments/{self.id}"
        if input_ is None:
            return self.gerrit.delete(endpoint)
        else:
            endpoint += "/delete"
            return self.gerrit.post(endpoint, json=input_, headers=self.gerrit.default_headers)


class GerritChangeRevisionComments(object):
    def __init__(self, change, revision, gerrit):
        self.change = change
        self.revision = revision
        self.gerrit = gerrit

    def list(self):
        """
        Lists the published comments of a revision.

        :return:
        """
        result = self.gerrit.get(f"/changes/{self.change}/revisions/{self.revision}/comments")
        comments = []
        for key, value in result.items():
            for item in value:
                comment = item
                comment.update({"path": key})
                comments.append(comment)
        return GerritChangeRevisionComment.parse_list(
            comments, change=self.change, revision=self.revision, gerrit=self.gerrit
        )

    def get(self, id_):
        """
        Retrieves a published comment of a revision.

        :param id_:
        :return:
        """
        result = self.gerrit.get(f"/changes/{self.change}/revisions/{self.revision}/comments/{id_}")
        return GerritChangeRevisionComment.parse(
            result, change=self.change, revision=self.revision, gerrit=self.gerrit
        )
