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
        if input_ is None:
            endpoint = "/changes/%s/revisions/%s/comments/%s" % (
                self.change,
                self.revision,
                self.id,
            )
            response = self.gerrit.requester.delete(
                self.gerrit.get_endpoint_url(endpoint)
            )
            result = self.gerrit.decode_response(response)
            return result
        else:
            endpoint = "/changes/%s/revisions/%s/comments/%s/delete" % (
                self.change,
                self.revision,
                self.id,
            )
            base_url = self.gerrit.get_endpoint_url(endpoint)
            response = self.gerrit.requester.post(
                base_url, json=input_, headers=self.gerrit.default_headers
            )
            result = self.gerrit.decode_response(response)
            return result


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
        endpoint = "/changes/%s/revisions/%s/comments" % (self.change, self.revision)
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
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
        endpoint = "/changes/%s/revisions/%s/comments/%s" % (
            self.change,
            self.revision,
            id_,
        )
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return GerritChangeRevisionComment.parse(
            result, change=self.change, revision=self.revision, gerrit=self.gerrit
        )
