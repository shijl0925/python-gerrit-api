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
        call_args = mock_change.gerrit.get.call_args
        assert "/votes/" in call_args[0][0]

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
        from tests.conftest import ACCOUNT_DATA
        mock_change.gerrit.delete.return_value = ACCOUNT_DATA
        result = mock_change.delete_assignee()
        mock_change.gerrit.delete.assert_called()
        assert result == ACCOUNT_DATA

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


# ---------------------------------------------------------------------------
# GerritChanges.create_change
# ---------------------------------------------------------------------------

class TestGerritChangesCreate:

    def test_create_change(self, mock_gerrit):
        from gerrit.changes.changes import GerritChanges
        from gerrit.changes.change import GerritChange

        input_ = {"project": "myProject", "branch": "master", "subject": "New change"}

        mock_project = MagicMock()
        mock_project.branches.get.return_value = MagicMock()
        mock_gerrit.projects.get.return_value = mock_project

        change_data = {
            "id": "myProject~master~I8473b95934b5732ac55d26311a706c9c2bde9940",
            "project": "myProject",
            "branch": "master",
            "change_id": "I8473b95934b5732ac55d26311a706c9c2bde9940",
            "subject": "New change",
            "status": "NEW",
            "created": "2013-02-01 09:59:32.126000000",
            "updated": "2013-02-01 09:59:32.126000000",
            "_number": 1235,
            "owner": {"_account_id": 1000096},
            "insertions": 0,
            "deletions": 0,
            "hashtags": [],
        }
        mock_gerrit.post.return_value = change_data

        changes = GerritChanges(gerrit=mock_gerrit)
        result = changes.create(input_=input_)
        mock_gerrit.post.assert_called_once()


# ---------------------------------------------------------------------------
# GerritChanges.get – multiple-changes fallback
# ---------------------------------------------------------------------------

class TestGerritChangesGetMultiple:

    def test_get_multiple_changes_found_raises(self, mock_gerrit):
        """When search returns >1 result, a GerritAPIException is raised."""
        from gerrit.changes.changes import GerritChanges
        from gerrit.utils.exceptions import GerritAPIException

        response_mock = MagicMock()
        response_mock.status_code = 404
        http_error = requests.exceptions.HTTPError(response=response_mock)

        # search returns two results → ambiguous
        mock_gerrit.get.side_effect = [
            http_error,
            [
                {"id": "myProject~master~I00001"},
                {"id": "myProject~master~I00002"},
            ],
        ]

        changes = GerritChanges(gerrit=mock_gerrit)
        with pytest.raises(GerritAPIException):
            changes.get(id_="Iambiguous")

    def test_get_non_404_error_raises(self, mock_gerrit):
        """Non-404 HTTPError from get() propagates as GerritAPIException."""
        from gerrit.changes.changes import GerritChanges
        from gerrit.utils.exceptions import GerritAPIException

        response_mock = MagicMock()
        response_mock.status_code = 500
        http_error = requests.exceptions.HTTPError(response=response_mock)
        mock_gerrit.get.side_effect = http_error

        changes = GerritChanges(gerrit=mock_gerrit)
        with pytest.raises(GerritAPIException):
            changes.get(id_="I12345")


# ---------------------------------------------------------------------------
# GerritChange additional methods
# ---------------------------------------------------------------------------

class TestGerritChangeAdditional:

    def test_get_detail_no_options(self, mock_change):
        mock_change.gerrit.get.return_value = {}
        mock_change.get_detail()
        mock_change.gerrit.get.assert_called()
        call_args = mock_change.gerrit.get.call_args
        assert call_args[1].get("params") is None

    def test_get_detail_with_options(self, mock_change):
        mock_change.gerrit.get.return_value = {}
        mock_change.get_detail(options=["LABELS"])
        call_args = mock_change.gerrit.get.call_args
        assert call_args[1]["params"] == {"o": ["LABELS"]}

    def test_get_meta_diff_with_old_and_meta(self, mock_change):
        mock_change.gerrit.get.return_value = {}
        mock_change.get_meta_diff(old="sha1", meta="sha2")
        call_args = mock_change.gerrit.get.call_args
        assert call_args[1]["params"]["old"] == "sha1"
        assert call_args[1]["params"]["meta"] == "sha2"

    def test_set_commit_message(self, mock_change):
        mock_change.gerrit.put.return_value = {}
        input_ = {"message": "Updated commit message\n\nChange-Id: I12345\n"}
        mock_change.set_commit_message(input_)
        mock_change.gerrit.put.assert_called()

    def test_remove_from_attention_set_no_input(self, mock_change):
        mock_change.remove_from_attention_set("kevin.shi")
        mock_change.gerrit.delete.assert_called()

    def test_remove_from_attention_set_with_input(self, mock_change):
        mock_change.remove_from_attention_set("kevin.shi", input_={"reason": "done"})
        mock_change.gerrit.post.assert_called()

    def test_get_edit_exists(self, mock_change):
        mock_change.gerrit.get.return_value = {"files": {}}
        from gerrit.changes.edit import GerritChangeEdit
        edit = mock_change.get_edit()
        assert isinstance(edit, GerritChangeEdit)

    def test_get_edit_not_found(self, mock_change):
        mock_change.gerrit.get.return_value = ""
        from gerrit.utils.exceptions import ChangeEditNotFoundError
        with pytest.raises(ChangeEditNotFoundError):
            mock_change.get_edit()

    def test_check_submit_requirement(self, mock_change):
        mock_change.gerrit.post.return_value = {"status": "SATISFIED"}
        input_ = {"submit_requirement": {"name": "Code-Review"}}
        result = mock_change.check_submit_requirement(input_)
        mock_change.gerrit.post.assert_called()

    def test_get_revision_current(self, mock_change):
        from gerrit.changes.revision import GerritChangeRevision
        revision = mock_change.get_revision()
        assert isinstance(revision, GerritChangeRevision)

    def test_get_revision_by_sha(self, mock_change):
        from gerrit.changes.revision import GerritChangeRevision
        revision = mock_change.get_revision(revision_id="abc123")
        assert isinstance(revision, GerritChangeRevision)

    def test_get_revision_by_positive_int(self, mock_change):
        """When revisions cache is empty, get_revision with positive int fetches revisions."""
        from gerrit.changes.revision import GerritChangeRevision

        # Simulate __get_revisions data: number 1 maps to sha "abc"
        mock_change.gerrit.get.return_value = [
            {
                "_number": 1234,
                "current_revision": "abcdef",
                "revisions": {
                    "abcdef": {"_number": 1}
                },
            }
        ]
        revision = mock_change.get_revision(revision_id=1)
        assert isinstance(revision, GerritChangeRevision)

    def test_get_revision_by_int_returns_none_when_not_found(self, mock_change):
        """Revision integer that doesn't exist in map returns None."""
        mock_change.gerrit.get.return_value = [
            {
                "_number": 1234,
                "current_revision": "abcdef",
                "revisions": {
                    "abcdef": {"_number": 1}
                },
            }
        ]
        result = mock_change.get_revision(revision_id=999)
        assert result is None

    def test_get_revision_by_negative_int(self, mock_change):
        """Negative revision_id is relative to current revision."""
        from gerrit.changes.revision import GerritChangeRevision

        mock_change.gerrit.get.return_value = [
            {
                "_number": 1234,
                "current_revision": "abcdef",
                "revisions": {
                    "aaaaaa": {"_number": 1},
                    "abcdef": {"_number": 2},
                },
            }
        ]
        # -1 relative to revision 2 → revision 1
        revision = mock_change.get_revision(revision_id=-1)
        assert isinstance(revision, GerritChangeRevision)


# ---------------------------------------------------------------------------
# GerritChangeEdit
# ---------------------------------------------------------------------------

class TestGerritChangeEdit:

    @pytest.fixture
    def mock_edit(self, mock_change):
        mock_change.gerrit.get.return_value = {"files": {}}
        from gerrit.changes.edit import GerritChangeEdit
        edit = GerritChangeEdit(change=mock_change.id, gerrit=mock_change.gerrit)
        return edit

    def test_edit_str(self, mock_edit, mock_change):
        assert str(mock_edit) == f"change {mock_change.id} edit"

    def test_get_change_file_content(self, mock_edit):
        mock_edit.gerrit.get.return_value = "base64content"
        result = mock_edit.get_change_file_content("README.md")
        mock_edit.gerrit.get.assert_called()
        assert result == "base64content"

    def test_get_file_meta_data(self, mock_edit):
        mock_edit.gerrit.get.return_value = {"name": "README.md"}
        result = mock_edit.get_file_meta_data("README.md")
        mock_edit.gerrit.get.assert_called()
        assert result["name"] == "README.md"

    def test_put_change_file_content(self, mock_edit):
        mock_edit.put_change_file_content("README.md", "new content")
        mock_edit.gerrit.put.assert_called_once()
        call_args = mock_edit.gerrit.put.call_args
        assert call_args[1]["data"] == "new content"

    def test_restore_file_content(self, mock_edit):
        mock_edit.restore_file_content("README.md")
        mock_edit.gerrit.post.assert_called_once()
        call_args = mock_edit.gerrit.post.call_args
        assert call_args[1]["json"]["restore_path"] == "README.md"

    def test_rename_file(self, mock_edit):
        mock_edit.rename_file("old.txt", "new.txt")
        mock_edit.gerrit.post.assert_called_once()
        call_args = mock_edit.gerrit.post.call_args
        assert call_args[1]["json"]["old_path"] == "old.txt"
        assert call_args[1]["json"]["new_path"] == "new.txt"

    def test_delete_file(self, mock_edit):
        mock_edit.delete_file("README.md")
        mock_edit.gerrit.delete.assert_called_once()

    def test_change_commit_message(self, mock_edit):
        input_ = {"message": "New message\n\nChange-Id: I123\n"}
        mock_edit.change_commit_message(input_)
        mock_edit.gerrit.put.assert_called_once()

    def test_get_commit_message(self, mock_edit):
        mock_edit.gerrit.get.return_value = "base64message"
        result = mock_edit.get_commit_message()
        assert result == "base64message"

    def test_publish(self, mock_edit):
        mock_edit.publish({"notify": "NONE"})
        mock_edit.gerrit.post.assert_called_once()

    def test_rebase(self, mock_edit):
        mock_edit.rebase()
        mock_edit.gerrit.post.assert_called_once()

    def test_delete(self, mock_edit):
        mock_edit.delete()
        mock_edit.gerrit.delete.assert_called_once()

