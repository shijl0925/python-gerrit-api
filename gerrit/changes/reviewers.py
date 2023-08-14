#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi

from gerrit.utils.models import BaseModel


class GerritChangeReviewer(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entity_name = "username"
        self.endpoint = f"/changes/{self.change}/reviewers/{self.username}"

    def delete(self, input_=None):
        """
        Deletes a reviewer from a change.
        Deleting a reviewer also removes that user from the attention set.

        .. code-block:: python

            input_ = {
                "notify": "NONE"
            }

            change = client.changes.get('Project~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            reviewer = change.reviewers.get('john.doe')
            reviewer.delete(input_)
            # or
            reviewer.delete()

        :param input_: the DeleteReviewerInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#delete-reviewer-input
        :return:
        """
        if input_ is None:
            self.gerrit.delete(self.endpoint)
        else:
            self.gerrit.post(self.endpoint + "/delete",
                             json=input_, headers=self.gerrit.default_headers)

    def list_votes(self):
        """
        Lists the votes for a specific reviewer of the change.

        :return:
        """
        return self.gerrit.get(self.endpoint + "/votes/")

    def delete_vote(self, label, input_=None):
        """
        Deletes a single vote from a change.
        Note, that even when the last vote of a reviewer is removed the reviewer itself is still
        listed on the change.

        .. code-block:: python

            input_ = {
                "notify": "NONE"
            }

            change = client.changes.get('Project~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            reviewer = change.reviewers.get('john.doe')
            reviewer.delete_vote('Code-Review', input_)
            # or
            reviewer.delete_vote('Code-Review')

        :param label:
        :param input_: the DeleteVoteInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#delete-vote-input
        :return:
        """
        endpoint = self.endpoint + f"/votes/{label}"
        if input_ is None:
            self.gerrit.delete(endpoint)
        else:
            self.gerrit.post(endpoint + "/delete", json=input_, headers=self.gerrit.default_headers)


class GerritChangeReviewers(object):
    def __init__(self, change, gerrit):
        self.change = change
        self.gerrit = gerrit
        self.endpoint = f"/changes/{self.change}/reviewers"

    def list(self):
        """
        Lists the reviewers of a change.

        :return:
        """
        result = self.gerrit.get(self.endpoint + "/")
        return GerritChangeReviewer.parse_list(result, change=self.change, gerrit=self.gerrit)

    def get(self, account):
        """
        Retrieves a reviewer of a change.

        :param account: _account_id, name, username or email
        :return:
        """
        result = self.gerrit.get(self.endpoint + f"/{account}")
        return GerritChangeReviewer(json=result[0], change=self.change, gerrit=self.gerrit)

    def add(self, input_):
        """
        Adds one user or all members of one group as reviewer to the change.

        Users can be moved from reviewer to CC and vice versa. This means if a user is added as
        CC that is already a reviewer on the change, the reviewer state of that user is updated
        to CC. If a user that is already a CC on the change is added as reviewer, the reviewer
        state of that user is updated to reviewer.

        Adding a new reviewer also adds that reviewer to the attention set, unless the change is
        work in progress. Also, moving a reviewer to CC removes that user from the attention set.

        .. code-block:: python

            input_ = {
                "reviewer": "john.doe"
            }

            change = client.changes.get('Project~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            new_reviewer = change.reviewers.add(input_)

        :param input_: the ReviewerInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#reviewer-input
        :return:
        """
        return self.gerrit.post(self.endpoint, json=input_, headers=self.gerrit.default_headers)
