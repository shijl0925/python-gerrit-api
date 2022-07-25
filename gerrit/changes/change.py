#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from packaging.version import parse
from gerrit.changes.reviewers import GerritChangeReviewers
from gerrit.changes.revision import GerritChangeRevision
from gerrit.changes.edit import GerritChangeEdit
from gerrit.changes.messages import GerritChangeMessages
from gerrit.utils.models import BaseModel
from gerrit.utils.exceptions import UnsupportMethod


class GerritChange(BaseModel):
    def __init__(self, **kwargs):
        self.revisions = {}
        self.current_revision_number = 0
        super(GerritChange, self).__init__(**kwargs)

    def create_merge_patch_set(self, input_):
        """
        Update an existing change by using a MergePatchSetInput entity.
        Gerrit will create a merge commit based on the information of MergePatchSetInput and add a new patch set to
        the change corresponding to the new merge commit.

        .. code-block:: python

            input_ = {
                "subject": "Merge master into stable",
                "merge": {
                  "source": "refs/heads/master"
                }
            }

            change = client.changes.get('myProject~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            result = change.update(input_)

        :param input_: the MergePatchSetInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#merge-patch-set-input
        :return:
        """
        endpoint = "/changes/%s/merge" % self.id
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.post(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def set_commit_message(self, input_):
        """
        Creates a new patch set with a new commit message.

        .. code-block:: python

            input_ = {
                "message": "New Commit message \\n\\nChange-Id: I10394472cbd17dd12454f229e4f6de00b143a444\\n"
            }

            change = client.changes.get('myProject~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            result = change.set_commit_message(input_)

        :param input_: the CommitMessageInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#commit-message-input
        :return:
        """
        endpoint = "/changes/%s/message" % self.id
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def list_votes(self, account):
        """
        Lists the votes for a specific reviewer of the change.

        :param account: account id or username
        :return:
        """
        endpoint = "/changes/%s/reviewers/%s/votes" % (self.id, account)
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def delete_vote(self, account, label, input_=None):
        """
        Deletes a single vote from a change. Note, that even when the last vote of a reviewer is removed the reviewer
        itself is still listed on the change.
        If another user removed a user’s vote, the user with the deleted vote will be added to the attention set.

        .. code-block:: python

            input_ = {
                "notify": "NONE"
            }

            change = client.changes.get('myProject~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            change.delete_vote('John', 'Code-Review', input_)
            # or
            change.delete_vote('John', 'Code-Review')

        :param account:
        :param label:
        :param input_: the DeleteVoteInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#delete-vote-input
        :return:
        """
        if input_ is None:
            endpoint = "/changes/%s/reviewers/%s/votes/%s" % (
                self.change,
                account,
                label,
            )
            self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))
        else:
            endpoint = "/changes/%s/reviewers/%s/votes/%s/delete" % (
                self.change,
                account,
                label,
            )
            base_url = self.gerrit.get_endpoint_url(endpoint)
            self.gerrit.requester.post(
                base_url, json=input_, headers=self.gerrit.default_headers
            )

    def get_topic(self):
        """
        Retrieves the topic of a change.

        :getter: Retrieves the topic of a change.
        :setter: Sets the topic of a change.
        :deleter: Deletes the topic of a change.

        :return:
        """
        endpoint = "/changes/%s/topic" % self.id
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def set_topic(self, topic):
        """
        Sets the topic of a change.

        :param topic: The new topic
        :return:
        """
        endpoint = "/changes/%s/topic" % self.id
        input_ = {"topic": topic}
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def delete_topic(self):
        """
        Deletes the topic of a change.

        :return:
        """
        endpoint = "/changes/%s/topic" % self.id
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))

    def get_assignee(self):
        """
        Retrieves the account of the user assigned to a change.

        :return:
        """
        endpoint = "/changes/%s/assignee" % self.id
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        if result:
            username = result.get("username")
            return self.gerrit.accounts.get(username)

    def set_assignee(self, input_):
        """
        Sets the assignee of a change.

        .. code-block:: python

            input_ = {
                "assignee": "jhon.doe"
            }

            change = client.changes.get('myProject~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            result = change.set_assignee(input_)

        :param input_: the AssigneeInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#assignee-input
        :return:
        """
        endpoint = "/changes/%s/assignee" % self.id
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        if result:
            username = result.get("username")
            return self.gerrit.accounts.get(username)

    def get_past_assignees(self):
        """
        Returns a list of every user ever assigned to a change, in the order in which they were first assigned.

        :return:
        """
        endpoint = "/changes/%s/past_assignees" % self.id
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        assignees = []
        if result:
            for item in result:
                username = item.get("username")
                assignee = self.gerrit.accounts.get(username)
                assignees.append(assignee)

        return assignees

    def delete_assignee(self):
        """
        Deletes the assignee of a change.

        :return:
        """
        endpoint = "/changes/%s/assignee" % self.id
        response = self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)

        if result:
            username = result.get("username")
            return self.gerrit.accounts.get(username)

    def get_pure_revert(self, commit):
        """
        Check if the given change is a pure revert of the change it references in revertOf.

        :param commit: commit id
        :return:
        """
        endpoint = "/changes/%s/pure_revert?o=%s" % (self.id, commit)
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def abandon(self):
        """
        Abandons a change.
        Abandoning a change also removes all users from the attention set.
        If the change cannot be abandoned because the change state doesn’t allow abandoning of the change,
        the response is “409 Conflict” and the error message is contained in the response body.

        :return:
        """
        endpoint = "/changes/%s/abandon" % self.id
        response = self.gerrit.requester.post(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def restore(self):
        """
        Restores a change.
        If the change cannot be restored because the change state doesn’t allow restoring the change,
        the response is “409 Conflict” and the error message is contained in the response body.

        :return:
        """
        endpoint = "/changes/%s/restore" % self.id
        response = self.gerrit.requester.post(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def rebase(self, input_):
        """
        Rebases a change.
        If the change cannot be rebased, e.g. due to conflicts, the response is '409 Conflict'
        and the error message is contained in the response body.

        .. code-block:: python

            input_ = {
                "base" : "1234",
            }

            change = client.changes.get('myProject~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            result = change.rebase(input_)

        :param input_: the RebaseInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#rebase-input
        :return:
        """
        endpoint = "/changes/%s/rebase" % self.id
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.post(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def move(self, input_):
        """
        Move a change.
        If the change cannot be moved because the change state doesn't allow moving the change,
        the response is '409 Conflict' and the error message is contained in the response body.

        .. code-block:: python

            input_ = {
                "destination_branch" : "release-branch"
            }

            change = client.changes.get('myProject~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            result = change.move(input_)

        :param input_: the MoveInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#move-input
        :return:
        """
        endpoint = "/changes/%s/move" % self.id
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.post(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def revert(self, input_=None):
        """
        Reverts a change.
        The request body does not need to include a RevertInput entity if no review comment is added.

        If the user doesn’t have revert permission on the change or upload permission on the destination branch,
        the response is '403 Forbidden', and the error message is contained in the response body.

        If the change cannot be reverted because the change state doesn't allow reverting the change,
        the response is 409 Conflict and the error message is contained in the response body.

        .. code-block:: python

            input_ = {
                "message" : "Message to be added as review comment to the change when reverting the change."
            }

            change = client.changes.get('myProject~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            result = change.revert()
            # or
            result = change.revert(input_)

        :param input_: the RevertInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#revert-input
        :return:
        """
        endpoint = "/changes/%s/revert" % self.id
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.post(
            base_url, json=input_ or {}, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def revert_submission(self):
        """
        Creates open revert changes for all of the changes of a certain submission.

        If the user doesn’t have revert permission on the change or upload permission on the destination,
        the response is '403 Forbidden', and the error message is contained in the response body.

        If the change cannot be reverted because the change state doesn’t allow reverting the change
        the response is '409 Conflict', and the error message is contained in the response body.

        :return:
        """
        version = self.gerrit.version
        if parse(version) < parse("3.2.0"):
            raise UnsupportMethod("The server does not support this method")

        endpoint = "/changes/%s/revert_submission" % self.id
        response = self.gerrit.requester.post(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def submit(self, input_):
        """
        Submits  a change.
        Submitting a change also removes all users from the attention set.

        If the change cannot be submitted because the submit rule doesn't allow submitting the change,
        the response is 409 Conflict and the error message is contained in the response body.

        .. code-block:: python

            input_ = {
                "on_behalf_of": 1001439
            }

            change = client.changes.get('myProject~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            result = change.submit(input_)

        :param input_: the SubmitInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#submit-input
        :return:
        """
        endpoint = "/changes/%s/submit" % self.id
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.post(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def delete(self):
        """
        Deletes a change.

        :return:
        """
        endpoint = "/changes/%s" % self.id
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))

    def get_include_in(self):
        """
        Retrieves the branches and tags in which a change is included.

        :return:
        """
        endpoint = "/changes/%s/in" % self.id
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def index(self):
        """
        Adds or updates the change in the secondary index.

        :return:
        """
        endpoint = "/changes/%s/index" % self.id
        self.gerrit.requester.post(self.gerrit.get_endpoint_url(endpoint))

    def list_comments(self):
        """
        Lists the published comments of all revisions of the change.

        :return:
        """
        endpoint = "/changes/%s/comments" % self.id
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def list_robot_comments(self):
        """
        Lists the robot comments of all revisions of the change.

        :return:
        """
        endpoint = "/changes/%s/robotcomments" % self.id
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def list_drafts(self):
        """
        Lists the draft comments of all revisions of the change that belong to the calling user.

        :return:
        """
        endpoint = "/changes/%s/drafts" % self.id
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def consistency_check(self):
        """
        Performs consistency checks on the change, and returns a ChangeInfo entity with the problems field set to
        a list of ProblemInfo entities.

        :return:
        """
        endpoint = "/changes/%s/check" % self.id
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def fix(self, input_=None):
        """
        Performs consistency checks on the change as with GET /check,
        and additionally fixes any problems that can be fixed automatically. The returned field values reflect any fixes.
        Some fixes have options controlling their behavior, which can be set in the FixInput entity body.
        Only the change owner, a project owner, or an administrator may fix changes.

        .. code-block:: python

            input_ = {
                "delete_patch_set_if_commit_missing": "true",
                "expect_merged_as": "something"
            }

            change = client.changes.get('myProject~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            result = change.fix()
            # or
            result = change.fix(input_)

        :param input_: the FixInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#fix-input
        :return:
        """
        endpoint = "/changes/%s/check" % self.id
        base_url = self.gerrit.get_endpoint_url(endpoint)
        if input_ is None:
            response = self.gerrit.requester.post(base_url)
        else:
            response = self.gerrit.requester.post(
                base_url, json=input_, headers=self.gerrit.default_headers
            )
        result = self.gerrit.decode_response(response)
        return result

    def set_work_in_progress(self, input_=None):
        """
        Marks the change as not ready for review yet.
        Changes may only be marked not ready by the owner, project owners or site administrators.
        Marking a change work in progress also removes all users from the attention set.

        The request body does not need to include a WorkInProgressInput entity if no review comment is added.

        .. code-block:: python

            input_ = {
                "message": "Refactoring needs to be done before we can proceed here."
            }

            change = client.changes.get('myProject~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            result = change.set_work_in_progress(input_)
            # or
            result = change.set_work_in_progress()

        :param input_: the WorkInProgressInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#work-in-progress-input
        :return:
        """
        endpoint = "/changes/%s/wip" % self.id
        base_url = self.gerrit.get_endpoint_url(endpoint)
        self.gerrit.requester.post(
            base_url, json=input_ or {}, headers=self.gerrit.default_headers
        )

    def set_ready_for_review(self, input_):
        """
        Marks the change as ready for review (set WIP property to false).
        Changes may only be marked ready by the owner, project owners or site administrators.
        Marking a change ready for review also adds all of the reviewers of the change to the attention set.

        .. code-block:: python

            input_ = {
                'message': 'Refactoring is done.'
            }

            change = client.changes.get('myProject~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            change.set_ready_for_review(input_)

        :param input_: the WorkInProgressInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#work-in-progress-input
        :return:
        """
        endpoint = "/changes/%s/ready" % self.id
        base_url = self.gerrit.get_endpoint_url(endpoint)
        self.gerrit.requester.post(
            base_url, json=input_, headers=self.gerrit.default_headers
        )

    def mark_private(self, input_):
        """
        Marks the change to be private. Only open changes can be marked private.
        Changes may only be marked private by the owner or site administrators.

        .. code-block:: python

            input_ = {
                "message": "After this security fix has been released we can make it public now."
            }
            change = client.changes.get('myProject~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            change.mark_private(input_)

        :param input_: the PrivateInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#private-input
        :return:
        """
        endpoint = "/changes/%s/private" % self.id
        base_url = self.gerrit.get_endpoint_url(endpoint)
        self.gerrit.requester.post(
            base_url, json=input_, headers=self.gerrit.default_headers
        )

    def unmark_private(self, input_=None):
        """
        Marks the change to be non-private. Note users can only unmark own private changes.
        If the change was already not private, the response is '409 Conflict'.

        .. code-block:: python

            input_ = {
                "message": "This is a security fix that must not be public."
            }
            change = client.changes.get('myProject~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            change.unmark_private(input_)
            # or
            change.unmark_private()

        :param input_: the PrivateInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#private-input
        :return:
        """
        if input_ is None:
            endpoint = "/changes/%s/private" % self.id
            self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))
        else:
            endpoint = "/changes/%s/private.delete" % self.id
            base_url = self.gerrit.get_endpoint_url(endpoint)
            self.gerrit.requester.post(
                base_url, json=input_, headers=self.gerrit.default_headers
            )

    def ignore(self):
        """
        Marks a change as ignored. The change will not be shown in the incoming reviews dashboard, and email
        notifications will be suppressed. Ignoring a change does not cause the change’s "updated" timestamp to be
        modified, and the owner is not notified.

        :return:
        """
        endpoint = "/changes/%s/ignore" % self.id
        self.gerrit.requester.put(self.gerrit.get_endpoint_url(endpoint))

    def unignore(self):
        """
        Un-marks a change as ignored.

        :return:
        """
        endpoint = "/changes/%s/unignore" % self.id
        self.gerrit.requester.put(self.gerrit.get_endpoint_url(endpoint))

    def mark_as_reviewed(self):
        """
        Marks a change as reviewed.

        :return:
        """
        endpoint = "/changes/%s/reviewed" % self.id
        self.gerrit.requester.put(self.gerrit.get_endpoint_url(endpoint))

    def mark_as_unreviewed(self):
        """
        Marks a change as unreviewed.

        :return:
        """
        endpoint = "/changes/%s/unreviewed" % self.id
        self.gerrit.requester.put(self.gerrit.get_endpoint_url(endpoint))

    def get_hashtags(self):
        """
        Gets the hashtags associated with a change.

        :return:
        """
        endpoint = "/changes/%s/hashtags" % self.id
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def set_hashtags(self, input_):
        """
        Adds and/or removes hashtags from a change.

        .. code-block:: python

            input_ = {
                "add" : [
                    "hashtag3"
                ],
                "remove" : [
                    "hashtag2"
                ]
            }
            change = client.changes.get('myProject~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            result = change.set_hashtags(input_)

        :param input_: the HashtagsInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#hashtags-input
        :return:
        """
        endpoint = "/changes/%s/hashtags" % self.id
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.post(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    @property
    def messages(self):
        return GerritChangeMessages(change=self.id, gerrit=self.gerrit)

    def get_edit(self):
        """
        Retrieves a change edit details.
        As response an EditInfo entity is returned that describes the change edit,
        or 204 No Content when change edit doesn't exist for this change.

        :return:
        """
        endpoint = "/changes/%s/edit" % self.id
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return GerritChangeEdit.parse(result, change=self.id, gerrit=self.gerrit)

    def create_empty_edit(self):
        """
        Creates empty change edit

        :return:
        """
        endpoint = "/changes/%s/edit" % self.id
        self.gerrit.requester.post(self.gerrit.get_endpoint_url(endpoint))

    @property
    def reviewers(self):
        return GerritChangeReviewers(change=self.id, gerrit=self.gerrit)

    def __get_revisions(self):
        endpoint = "/changes/?q=%s&o=ALL_REVISIONS" % self.number
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        [result] = self.gerrit.decode_response(response)
        self.revisions = {}
        for revision_sha, revision in result["revisions"].items():
            if result["current_revision"] == revision_sha:
                self.current_revision_number = revision["_number"]
            self.revisions[revision["_number"]] = revision_sha

    def __revision_number_to_sha(self, number):
        if number in self.revisions:
            return self.revisions[number]
        return None

    def get_revision(self, revision_id="current"):
        """
        Get one revision by revision SHA or integer number.

        :param revision_id: Optional ID. If not specified, the current revision will be retrieved.
                            It supports SHA IDs and integer numbers from -X to +X, where X is the
                            current (latest) revision.
                            Zero means current revision.
                            -N means the current revision number X minus N, so if the current
                            revision is 50, and -1 is given, the revision 49 will be retrieved.
        :return:
        """
        if isinstance(revision_id, int):
            if len(self.revisions) == 0:
                self.__get_revisions()
            if revision_id <= 0:
                revision_id = self.current_revision_number + revision_id
            revision_id = self.__revision_number_to_sha(revision_id)
            if revision_id is None:
                return None

        return GerritChangeRevision(
            gerrit=self.gerrit,
            project=self.project,
            change=self.id,
            revision=revision_id
        )

    def get_attention_set(self):
        """
        Returns all users that are currently in the attention set.
        support this method since v3.3.0

        :return:
        """
        version = self.gerrit.version
        if parse(version) < parse("3.3.0"):
            raise UnsupportMethod("The server does not support this method")

        endpoint = "/changes/%s/attention" % self.id
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def add_to_attention_set(self, input_):
        """
        Adds a single user to the attention set of a change.
        support this method since v3.3.0

        A user can only be added if they are not in the attention set.
        If a user is added while already in the attention set, the request is silently ignored.

        .. code-block:: python

            input_ = {
                "user": "John Doe",
                "reason": "reason"
            }
            change = client.changes.get('myProject~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            result = change.add_to_attention_set(input_)

        :param input_: the AttentionSetInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#attention-set-input
        :return:
        """
        version = self.gerrit.version
        if parse(version) < parse("3.3.0"):
            raise UnsupportMethod("The server does not support this method")

        endpoint = "/changes/%s/attention" % self.id
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.post(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def remove_from_attention_set(self, id_, input_=None):
        """
        Deletes a single user from the attention set of a change.
        support this method since v3.3.0

        A user can only be removed from the attention set.
        if they are currently in the attention set. Otherwise, the request is silently ignored.

        .. code-block:: python

            input_ = {
                "reason": "reason"
            }
            change = client.changes.get('myProject~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            change.remove_from_attention_set('kevin.shi', input_)
            # or
            change.remove_from_attention_set('kevin.shi')

        :param id_: account id
        :param input_: the AttentionSetInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#attention-set-input
        :return:
        """
        version = self.gerrit.version
        if parse(version) < parse("3.3.0"):
            raise UnsupportMethod("The server does not support this method")

        if input_ is None:
            endpoint = "/changes/%s/attention/%s" % (self.id, id_)
            self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))
        else:
            endpoint = "/changes/%s/attention/%s/delete" % (self.id, id_)
            base_url = self.gerrit.get_endpoint_url(endpoint)
            response = self.gerrit.requester.post(
                base_url, json=input_, headers=self.gerrit.default_headers
            )
            result = self.gerrit.decode_response(response)
            return result
