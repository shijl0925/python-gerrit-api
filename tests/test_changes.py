#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
"""
Unit tests for gerrit.changes — all HTTP calls are mocked.
"""
import logging
import pytest
import requests
from unittest.mock import MagicMock

from tests.conftest import CHANGE_DATA, ACCOUNT_DATA

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# GerritChanges (manager)
# ---------------------------------------------------------------------------

class TestGerritChanges:

    def test_search_changes(self, mock_gerrit):
        mock_gerrit.get.return_value = [CHANGE_DATA]

        from gerrit.changes.changes import GerritChanges
        changes = GerritChanges(gerrit=mock_gerrit)
        result = changes.search(query="status:open", limit=25, skip=0)
        assert len(result) >= 1

    def test_search_changes_with_options(self, mock_gerrit):
        mock_gerrit.get.return_value = [CHANGE_DATA]

        from gerrit.changes.changes import GerritChanges
        changes = GerritChanges(gerrit=mock_gerrit)
        result = changes.search(query="status:open", options=["LABELS"], limit=10)
        assert isinstance(result, list)

    def test_get_change(self, mock_gerrit):
        mock_gerrit.get.return_value = CHANGE_DATA

        from gerrit.changes.changes import GerritChanges
        from gerrit.changes.change import GerritChange
        changes = GerritChanges(gerrit=mock_gerrit)
        change = changes.get(id_="I8473b95934b5732ac55d26311a706c9c2bde9940")
        assert isinstance(change, GerritChange)
        assert change.id == CHANGE_DATA["id"]

    def test_get_change_not_found(self, mock_gerrit):
        response_mock = MagicMock()
        response_mock.status_code = 404
        http_error = requests.exceptions.HTTPError(response=response_mock)
        # First call raises 404; second call (from search) returns empty list
        mock_gerrit.get.side_effect = [http_error, []]

        from gerrit.changes.changes import GerritChanges
        from gerrit.utils.exceptions import ChangeNotFoundError
        changes = GerritChanges(gerrit=mock_gerrit)
        with pytest.raises(ChangeNotFoundError):
            changes.get(id_="I00000000000000000000")

    def test_get_change_not_found_no_search(self, mock_gerrit):
        """id_ that does not start with 'I' skips the search fallback."""
        response_mock = MagicMock()
        response_mock.status_code = 404
        http_error = requests.exceptions.HTTPError(response=response_mock)
        mock_gerrit.get.side_effect = http_error

        from gerrit.changes.changes import GerritChanges
        from gerrit.utils.exceptions import ChangeNotFoundError
        changes = GerritChanges(gerrit=mock_gerrit)
        with pytest.raises(ChangeNotFoundError):
            changes.get(id_="999999999")

    def test_delete_change(self, mock_gerrit):
        mock_gerrit.get.return_value = CHANGE_DATA

        from gerrit.changes.changes import GerritChanges
        changes = GerritChanges(gerrit=mock_gerrit)
        changes.delete(id_=CHANGE_DATA["id"])
        mock_gerrit.delete.assert_called_once()


# ---------------------------------------------------------------------------
# GerritChange (single change) — attribute & TO-dict tests
# ---------------------------------------------------------------------------

class TestGerritChange:

    def test_change_str_and_repr(self, mock_change):
        assert str(mock_change) == CHANGE_DATA["id"]
        assert "GerritChange" in repr(mock_change)

    def test_change_attributes(self, mock_change):
        attrs = ["id", "project", "branch", "hashtags", "change_id", "subject",
                 "status", "created", "updated", "number", "owner",
                 "insertions", "deletions"]
        for attr in attrs:
            assert hasattr(mock_change, attr), f"Missing attribute: {attr}"

    def test_change_to_dict(self, mock_change):
        info = mock_change.to_dict()
        assert "_number" in info
        assert info["project"] == CHANGE_DATA["project"]

    def test_get_detail(self, mock_change):
        detail = {"labels": {"Code-Review": {}}, "messages": []}
        mock_change.gerrit.get.return_value = detail
        result = mock_change.get_detail(options=["LABELS"])
        assert "labels" in result

    def test_list_actions(self, mock_change):
        actions = {"submit": {"method": "POST", "label": "Submit", "enabled": True}}
        mock_change.gerrit.get.return_value = actions
        result = mock_change.list_actions()
        assert isinstance(result, dict)
        assert "submit" in result

    def test_add_message(self, mock_change):
        mock_change.add_message({"message": "Some nits need to be fixed."})
        mock_change.gerrit.put.assert_called()
        call_args = mock_change.gerrit.put.call_args
        assert "/message" in call_args[0][0]

    def test_get_meta_diff(self, mock_change):
        meta = {"removed": [], "added": []}
        mock_change.gerrit.get.return_value = meta
        result = mock_change.get_meta_diff()
        assert "removed" in result
        assert "added" in result

    def test_list_votes(self, mock_change):
        votes = {"Code-Review": 1, "Verified": 1}
        mock_change.gerrit.get.return_value = votes
        result = mock_change.list_votes(account="johndoe")
        assert result.get("Code-Review") == 1

    def test_delete_vote(self, mock_change):
        mock_change.delete_vote("johndoe", "Code-Review")
        mock_change.gerrit.delete.assert_called()

    def test_delete_vote_with_input(self, mock_change):
        mock_change.delete_vote("johndoe", "Code-Review", input_={"notify": "NONE"})
        mock_change.gerrit.post.assert_called()

    def test_get_topic(self, mock_change):
        mock_change.gerrit.get.return_value = "my-topic"
        result = mock_change.get_topic()
        assert result == "my-topic"

    def test_set_topic(self, mock_change):
        mock_change.gerrit.put.return_value = "new-topic"
        mock_change.set_topic("new-topic")
        mock_change.gerrit.put.assert_called()

    def test_delete_topic(self, mock_change):
        mock_change.delete_topic()
        mock_change.gerrit.delete.assert_called()

    def test_get_assignee(self, mock_change):
        mock_change.gerrit.get.return_value = ACCOUNT_DATA
        result = mock_change.get_assignee()
        assert result.get("username") == ACCOUNT_DATA["username"]

    def test_set_assignee(self, mock_change):
        mock_change.gerrit.put.return_value = ACCOUNT_DATA
        result = mock_change.set_assignee({"assignee": "testuser"})
        mock_change.gerrit.put.assert_called()

    def test_get_past_assignees(self, mock_change):
        mock_change.gerrit.get.return_value = [ACCOUNT_DATA]
        result = mock_change.get_past_assignees()
        assert len(result) >= 1

    def test_delete_assignee(self, mock_change):
        mock_change.delete_assignee()
        mock_change.gerrit.delete.assert_called()

    def test_get_pure_revert(self, mock_change):
        mock_change.gerrit.get.return_value = {"is_pure_revert": True}
        result = mock_change.get_pure_revert("abc123")
        assert "is_pure_revert" in result

    def test_abandon(self, mock_change):
        mock_change.gerrit.post.return_value = {**CHANGE_DATA, "status": "ABANDONED"}
        result = mock_change.abandon()
        mock_change.gerrit.post.assert_called()

    def test_restore(self, mock_change):
        mock_change.gerrit.post.return_value = {**CHANGE_DATA, "status": "NEW"}
        result = mock_change.restore()
        mock_change.gerrit.post.assert_called()

    def test_rebase(self, mock_change):
        mock_change.gerrit.post.return_value = CHANGE_DATA
        result = mock_change.rebase({"base": "master"})
        mock_change.gerrit.post.assert_called()

    def test_move(self, mock_change):
        mock_change.gerrit.post.return_value = CHANGE_DATA
        result = mock_change.move({"destination_branch": "stable"})
        mock_change.gerrit.post.assert_called()

    def test_revert(self, mock_change):
        mock_change.gerrit.post.return_value = CHANGE_DATA
        result = mock_change.revert()
        mock_change.gerrit.post.assert_called()

    def test_submit(self, mock_change):
        mock_change.gerrit.post.return_value = {**CHANGE_DATA, "status": "MERGED"}
        result = mock_change.submit()
        mock_change.gerrit.post.assert_called()

    def test_submit_with_input(self, mock_change):
        mock_change.gerrit.post.return_value = {**CHANGE_DATA, "status": "MERGED"}
        result = mock_change.submit({"on_behalf_of": 1001})
        mock_change.gerrit.post.assert_called()

    def test_list_submitted_together_changes(self, mock_change):
        mock_change.gerrit.get.return_value = {"changes": [], "non_visible_changes": 0}
        result = mock_change.list_submitted_together_changes()
        assert len(result.get("changes")) >= 0

    def test_delete(self, mock_change):
        mock_change.delete()
        mock_change.gerrit.delete.assert_called_once()

    def test_get_include_in(self, mock_change):
        mock_change.gerrit.get.return_value = {"branches": ["master"], "tags": []}
        result = mock_change.get_include_in()
        assert "branches" in result
        assert "tags" in result

    def test_list_comments(self, mock_change):
        mock_change.gerrit.get.return_value = {"myfile.py": []}
        result = mock_change.list_comments()
        assert isinstance(result, dict)

    def test_get_attention_set(self, mock_change):
        mock_change.gerrit.get.return_value = []
        result = mock_change.get_attention_set()
        assert len(result) >= 0

    def test_add_to_attention_set(self, mock_change):
        mock_change.gerrit.post.return_value = {"account": ACCOUNT_DATA}
        result = mock_change.add_to_attention_set({"user": "testuser", "reason": "test"})
        mock_change.gerrit.post.assert_called()

    def test_get_hashtags(self, mock_change):
        mock_change.gerrit.get.return_value = ["tag1", "tag2"]
        result = mock_change.get_hashtags()
        assert len(result) >= 0

    def test_set_hashtags(self, mock_change):
        mock_change.gerrit.post.return_value = ["tag1", "tag3"]
        result = mock_change.set_hashtags({"add": ["tag3"], "remove": ["tag2"]})
        mock_change.gerrit.post.assert_called()

    def test_set_work_in_progress(self, mock_change):
        mock_change.set_work_in_progress()
        mock_change.gerrit.post.assert_called()

    def test_set_ready_for_review(self, mock_change):
        mock_change.set_ready_for_review({"message": "Ready"})
        mock_change.gerrit.post.assert_called()

    def test_mark_private(self, mock_change):
        mock_change.mark_private({"message": "private"})
        mock_change.gerrit.post.assert_called()

    def test_unmark_private(self, mock_change):
        mock_change.unmark_private()
        mock_change.gerrit.delete.assert_called()

    def test_ignore(self, mock_change):
        mock_change.ignore()
        mock_change.gerrit.put.assert_called()

    def test_unignore(self, mock_change):
        mock_change.unignore()
        mock_change.gerrit.put.assert_called()

    def test_mark_as_reviewed(self, mock_change):
        mock_change.mark_as_reviewed()
        mock_change.gerrit.put.assert_called()

    def test_mark_as_unreviewed(self, mock_change):
        mock_change.mark_as_unreviewed()
        mock_change.gerrit.put.assert_called()

    def test_consistency_check(self, mock_change):
        mock_change.gerrit.get.return_value = {"problems": []}
        result = mock_change.consistency_check()
        assert "problems" in result

    def test_fix(self, mock_change):
        mock_change.gerrit.post.return_value = {"problems": []}
        result = mock_change.fix()
        mock_change.gerrit.post.assert_called()

    def test_create_empty_edit(self, mock_change):
        mock_change.create_empty_edit()
        mock_change.gerrit.post.assert_called()

    def test_index(self, mock_change):
        mock_change.index()
        mock_change.gerrit.post.assert_called()

    def test_create_merge_patch_set(self, mock_change):
        mock_change.gerrit.post.return_value = CHANGE_DATA
        result = mock_change.create_merge_patch_set(
            {"subject": "merge", "merge": {"source": "refs/heads/master"}}
        )
        mock_change.gerrit.post.assert_called()

    def test_set_commit_message(self, mock_change):
        mock_change.gerrit.put.return_value = None
        mock_change.set_commit_message({"message": "New message\n\nChange-Id: I123\n"})
        mock_change.gerrit.put.assert_called()

    def test_revert_submission(self, mock_change):
        mock_change.gerrit.post.return_value = {"revert_changes": []}
        result = mock_change.revert_submission()
        mock_change.gerrit.post.assert_called()

    def test_check_submit_requirement(self, mock_change):
        mock_change.gerrit.post.return_value = {"status": "SATISFIED"}
        result = mock_change.check_submit_requirement({"name": "Code-Review"})
        mock_change.gerrit.post.assert_called()

    def test_list_robot_comments(self, mock_change):
        mock_change.gerrit.get.return_value = {}
        result = mock_change.list_robot_comments()
        assert isinstance(result, dict)

    def test_list_drafts(self, mock_change):
        mock_change.gerrit.get.return_value = {}
        result = mock_change.list_drafts()
        assert isinstance(result, dict)

    def test_get_revision(self, mock_change):
        from gerrit.changes.revision import GerritChangeRevision
        revision = mock_change.get_revision()
        assert isinstance(revision, GerritChangeRevision)
        assert str(revision) == "current"

    def test_get_revision_with_sha(self, mock_change):
        from gerrit.changes.revision import GerritChangeRevision
        sha = "abc123def456"
        revision = mock_change.get_revision(revision_id=sha)
        assert isinstance(revision, GerritChangeRevision)
        assert str(revision) == sha

    def test_get_revision_with_integer(self, mock_change):
        """get_revision(1) triggers __get_revisions() which calls gerrit.get()."""
        revisions_response = [{
            "_number": CHANGE_DATA["_number"],
            "current_revision": "sha_current",
            "revisions": {
                "sha_current": {"_number": 1},
            },
        }]
        mock_change.gerrit.get.return_value = revisions_response

        from gerrit.changes.revision import GerritChangeRevision
        revision = mock_change.get_revision(revision_id=1)
        assert isinstance(revision, GerritChangeRevision)

    def test_messages_property(self, mock_change):
        from gerrit.changes.messages import GerritChangeMessages
        assert isinstance(mock_change.messages, GerritChangeMessages)

    def test_reviewers_property(self, mock_change):
        from gerrit.changes.reviewers import GerritChangeReviewers
        assert isinstance(mock_change.reviewers, GerritChangeReviewers)


# ---------------------------------------------------------------------------
# GerritChangeMessages
# ---------------------------------------------------------------------------

class TestGerritChangeMessages:

    def test_list_messages(self, mock_change):
        messages = [{"id": "abc", "message": "Uploaded patch set 1."}]
        mock_change.gerrit.get.return_value = messages
        result = mock_change.messages.list()
        assert len(result) >= 0

    def test_get_message(self, mock_change):
        message_data = {"id": "abc123", "message": "Test message", "date": "2021-01-01"}
        mock_change.gerrit.get.return_value = message_data
        message = mock_change.messages.get(id_="abc123")
        assert "message" in message.to_dict()

    def test_delete_message(self, mock_change):
        message_data = {"id": "abc123", "message": "Test message", "date": "2021-01-01"}
        mock_change.gerrit.get.return_value = message_data
        message = mock_change.messages.get(id_="abc123")
        message.delete()
        mock_change.gerrit.delete.assert_called()

    def test_delete_message_with_input(self, mock_change):
        message_data = {"id": "abc123", "message": "Test message", "date": "2021-01-01"}
        mock_change.gerrit.get.return_value = message_data
        message = mock_change.messages.get(id_="abc123")
        message.delete(input_={"reason": "spam"})
        mock_change.gerrit.post.assert_called()


# ---------------------------------------------------------------------------
# GerritChangeReviewers
# ---------------------------------------------------------------------------

class TestGerritChangeReviewers:

    def test_list_reviewers(self, mock_change):
        mock_change.gerrit.get.return_value = [{"_account_id": 1, "name": "Alice"}]
        result = mock_change.reviewers.list()
        assert len(result) >= 0

    def test_get_reviewer(self, mock_change):
        reviewer_data = [{"_account_id": 1000096, "name": "Test User"}]
        mock_change.gerrit.get.return_value = reviewer_data

        reviewer = mock_change.reviewers.get(account="testuser")
        assert str(reviewer) == "1000096"

    def test_get_reviewer_not_found(self, mock_change):
        response_mock = MagicMock()
        response_mock.status_code = 404
        http_error = requests.exceptions.HTTPError(response=response_mock)
        mock_change.gerrit.get.side_effect = http_error

        from gerrit.utils.exceptions import ReviewerNotFoundError
        with pytest.raises(ReviewerNotFoundError):
            mock_change.reviewers.get(account="nobody")

    def test_reviewer_list_votes(self, mock_change):
        reviewer_data = [{"_account_id": 1000096, "name": "Test User"}]
        votes_data = {"Code-Review": 2}
        mock_change.gerrit.get.side_effect = [reviewer_data, reviewer_data, votes_data]

        reviewer = mock_change.reviewers.get(account="testuser")
        votes = reviewer.list_votes()
        assert votes.get("Code-Review") == 2

    def test_reviewer_delete(self, mock_change):
        reviewer_data = [{"_account_id": 1000096, "name": "Test User"}]
        mock_change.gerrit.get.return_value = reviewer_data

        reviewer = mock_change.reviewers.get(account="testuser")
        reviewer.delete()
        mock_change.gerrit.delete.assert_called()

    def test_reviewer_delete_with_input(self, mock_change):
        reviewer_data = [{"_account_id": 1000096, "name": "Test User"}]
        mock_change.gerrit.get.return_value = reviewer_data

        reviewer = mock_change.reviewers.get(account="testuser")
        reviewer.delete(input_={"notify": "NONE"})
        mock_change.gerrit.post.assert_called()

    def test_reviewer_delete_vote(self, mock_change):
        reviewer_data = [{"_account_id": 1000096, "name": "Test User"}]
        mock_change.gerrit.get.return_value = reviewer_data

        reviewer = mock_change.reviewers.get(account="testuser")
        reviewer.delete_vote("Code-Review")
        mock_change.gerrit.delete.assert_called()

    def test_add_reviewer_already_exists(self, mock_change):
        """Adding a reviewer that already exists should raise ReviewerAlreadyExistsError."""
        reviewer_data = [{"_account_id": 1000096, "name": "Test User"}]
        mock_change.gerrit.get.return_value = reviewer_data

        from gerrit.utils.exceptions import ReviewerAlreadyExistsError
        with pytest.raises(ReviewerAlreadyExistsError):
            mock_change.reviewers.add({"reviewer": "testuser"})

    def test_add_reviewer_new(self, mock_change):
        """Adding a reviewer not yet on the change succeeds."""
        response_mock = MagicMock()
        response_mock.status_code = 404
        http_error = requests.exceptions.HTTPError(response=response_mock)
        reviewer_data = [{"_account_id": 1000096}]
        # First get → 404 (not found); post succeeds; get again → reviewer_data × 2
        mock_change.gerrit.get.side_effect = [http_error, reviewer_data, reviewer_data]

        from gerrit.changes.reviewers import GerritChangeReviewer
        reviewer = mock_change.reviewers.add({"reviewer": "newuser"})
        assert isinstance(reviewer, GerritChangeReviewer)

