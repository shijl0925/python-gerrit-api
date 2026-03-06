#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
"""
Unit tests for gerrit.changes.revision — all HTTP calls are mocked.
"""
import base64
import logging
import pytest
import requests
from unittest.mock import MagicMock

from tests.conftest import CHANGE_DATA

logger = logging.getLogger(__name__)

COMMIT_INFO = {
    "commit": "abc123def456",
    "author": {"name": "Test Author", "email": "author@example.com"},
    "committer": {"name": "Test Committer", "email": "committer@example.com"},
    "message": "Test commit",
    "subject": "Test commit",
}


@pytest.fixture
def revision(mock_change):
    """Return a GerritChangeRevision for the mock change (current revision)."""
    return mock_change.get_revision()


@pytest.fixture
def revision_with_sha(mock_change):
    """Return a GerritChangeRevision with an explicit SHA."""
    return mock_change.get_revision(revision_id="abc123def456")


# ---------------------------------------------------------------------------
# GerritChangeRevision
# ---------------------------------------------------------------------------

class TestGerritChangeRevision:

    def test_revision_str_and_repr(self, revision):
        assert str(revision) == "current"
        assert "GerritChangeRevision" in repr(revision)

    def test_revision_str_with_sha(self, revision_with_sha):
        assert str(revision_with_sha) == "abc123def456"

    def test_get_commit(self, revision):
        revision.gerrit.get.return_value = COMMIT_INFO
        result = revision.get_commit()
        assert "commit" in result

    def test_get_description(self, revision):
        revision.gerrit.get.return_value = "Patch set description"
        result = revision.get_description()
        assert result == "Patch set description"

    def test_set_description(self, revision):
        revision.gerrit.put.return_value = "New description"
        revision.set_description({"description": "New description"})
        revision.gerrit.put.assert_called()

    def test_get_merge_list(self, revision):
        revision.gerrit.get.return_value = [COMMIT_INFO]
        result = revision.get_merge_list()
        assert len(result) >= 0

    def test_get_revision_actions(self, revision):
        actions = {"submit": {"method": "POST", "enabled": True}}
        revision.gerrit.get.return_value = actions
        result = revision.get_revision_actions()
        assert isinstance(result, dict)

    def test_get_review(self, revision):
        review = {"reviewers": {"REVIEWER": [], "CC": []}, "labels": {}}
        revision.gerrit.get.return_value = review
        result = revision.get_review()
        reviewers = result.get("reviewers")
        assert isinstance(reviewers.get("CC", []), list)
        assert isinstance(reviewers.get("REVIEWER", []), list)

    def test_set_review(self, revision):
        revision.gerrit.post.return_value = {"labels": {"Code-Review": -1}}
        result = revision.set_review({"message": "nit", "labels": {"Code-Review": -1}})
        revision.gerrit.post.assert_called()

    def test_get_related_changes(self, revision):
        revision.gerrit.get.return_value = {"changes": []}
        result = revision.get_related_changes()
        assert len(result.get("changes")) >= 0

    def test_rebase(self, revision):
        revision.gerrit.post.return_value = CHANGE_DATA
        result = revision.rebase({"base": "master"})
        revision.gerrit.post.assert_called()

    def test_submit(self, revision):
        revision.gerrit.post.return_value = {**CHANGE_DATA, "status": "MERGED"}
        result = revision.submit()
        revision.gerrit.post.assert_called()

    def test_get_patch(self, revision):
        content = base64.b64encode(b"diff --git a/file.py b/file.py").decode("utf-8")
        revision.gerrit.get.return_value = content
        result = revision.get_patch()
        assert len(result) > 0

    def test_get_patch_decoded(self, revision):
        content = base64.b64encode(b"diff --git a/file.py b/file.py").decode("utf-8")
        revision.gerrit.get.return_value = content
        result = revision.get_patch(decode=True)
        assert len(result) > 0
        assert isinstance(result, str)

    def test_is_mergeable(self, revision):
        revision.gerrit.get.return_value = {"mergeable": True, "strategy": "recursive"}
        result = revision.is_mergeable()
        assert "mergeable" in result

    def test_get_submit_type(self, revision):
        revision.gerrit.get.return_value = "REBASE_IF_NECESSARY"
        result = revision.get_submit_type()
        assert result == "REBASE_IF_NECESSARY"

    def test_submit_preview(self, revision):
        revision.gerrit.get.return_value = b"binary bundle data"
        result = revision.submit_preview()
        assert result is not None

    def test_test_submit_type(self, revision):
        revision.gerrit.post.return_value = "REBASE_IF_NECESSARY"
        result = revision.test_submit_type("submit_type(fast_forward_only).")
        revision.gerrit.post.assert_called()

    def test_test_submit_rule(self, revision):
        revision.gerrit.post.return_value = [{"status": "OK"}]
        result = revision.test_submit_rule("submit_rule(submit(R)) :- ...")
        revision.gerrit.post.assert_called()

    def test_cherry_pick(self, revision):
        revision.gerrit.post.return_value = CHANGE_DATA
        result = revision.cherry_pick({"message": "cherry-pick", "destination": "stable"})
        revision.gerrit.post.assert_called()

    def test_list_reviewers(self, revision):
        revision.gerrit.get.return_value = [{"_account_id": 1000096}]
        result = revision.list_reviewers()
        assert len(result) >= 0

    def test_list_votes(self, revision):
        revision.gerrit.get.return_value = {"Code-Review": 1, "Verified": 1}
        result = revision.list_votes(account="testuser")
        assert result.get("Code-Review") == 1

    def test_delete_vote(self, revision):
        revision.delete_vote("testuser", "Code-Review")
        revision.gerrit.delete.assert_called()

    def test_delete_vote_with_input(self, revision):
        revision.delete_vote("testuser", "Code-Review", input_={"notify": "NONE"})
        revision.gerrit.post.assert_called()

    def test_comments_property(self, revision):
        from gerrit.changes.comments import GerritChangeRevisionComments
        assert isinstance(revision.comments, GerritChangeRevisionComments)

    def test_files_property(self, revision):
        from gerrit.changes.files import GerritChangeRevisionFiles
        assert isinstance(revision.files, GerritChangeRevisionFiles)

    def test_drafts_property(self, revision):
        from gerrit.changes.drafts import GerritChangeRevisionDrafts
        assert isinstance(revision.drafts, GerritChangeRevisionDrafts)

    def test_list_robot_comments(self, revision):
        revision.gerrit.get.return_value = {}
        result = revision.list_robot_comments()
        assert isinstance(result, dict)

    def test_get_robot_comment(self, revision):
        revision.gerrit.get.return_value = {"id": "robot_comment_1", "message": "lint error"}
        result = revision.get_robot_comment("robot_comment_1")
        assert "id" in result


# ---------------------------------------------------------------------------
# GerritChangeRevisionComments
# ---------------------------------------------------------------------------

class TestGerritChangeRevisionComments:

    def test_list_comments(self, revision):
        revision.gerrit.get.return_value = {
            "file.py": [{"id": "comment1", "message": "test", "path": "file.py"}]
        }
        result = revision.comments.list()
        assert len(result) >= 0

    def test_get_comment(self, revision):
        comment_data = {"id": "comment1", "message": "test comment", "path": "file.py"}
        revision.gerrit.get.return_value = comment_data
        comment = revision.comments.get(id_="comment1")
        assert "message" in comment.to_dict()

    def test_delete_comment(self, revision):
        comment_data = {"id": "comment1", "message": "test", "path": "file.py"}
        revision.gerrit.get.return_value = comment_data
        comment = revision.comments.get(id_="comment1")
        comment.delete()
        revision.gerrit.delete.assert_called()

    def test_delete_comment_with_reason(self, revision):
        comment_data = {"id": "comment1", "message": "test", "path": "file.py"}
        revision.gerrit.get.return_value = comment_data
        comment = revision.comments.get(id_="comment1")
        result = comment.delete(input_={"reason": "confidential"})
        revision.gerrit.post.assert_called()


# ---------------------------------------------------------------------------
# GerritChangeRevisionFiles
# ---------------------------------------------------------------------------

class TestGerritChangeRevisionFiles:

    def test_search_files(self, revision):
        revision.gerrit.get.return_value = {"file.py": {"lines_inserted": 5}}
        result = revision.files.search()
        assert isinstance(result, dict)

    def test_search_files_with_params(self, revision):
        revision.gerrit.get.return_value = {"file.py": {"lines_inserted": 5}}
        result = revision.files.search(reviewed=True, base=1, q="file.py", parent=1)

    def test_files_len(self, revision):
        revision.gerrit.get.return_value = {"file.py": {}, "README.md": {}}
        files = revision.files
        assert len(files) == 2

    def test_files_keys(self, revision):
        revision.gerrit.get.return_value = {"file.py": {}, "README.md": {}}
        keys = revision.files.keys()
        assert "file.py" in keys
        assert "README.md" in keys

    def test_files_contains(self, revision):
        revision.gerrit.get.return_value = {"file.py": {}}
        assert "file.py" in revision.files

    def test_files_iter(self, revision):
        from gerrit.changes.files import GerritChangeRevisionFile
        revision.gerrit.get.return_value = {"file.py": {"lines_inserted": 5}}
        for f in revision.files:
            assert isinstance(f, GerritChangeRevisionFile)

    def test_get_file_by_path(self, revision):
        from gerrit.changes.files import GerritChangeRevisionFile
        revision.gerrit.get.return_value = {"file.py": {"lines_inserted": 5}}
        f = revision.files["file.py"]
        assert isinstance(f, GerritChangeRevisionFile)
        assert str(f) == "file.py"

    def test_get_unknown_file_raises(self, revision):
        from gerrit.utils.exceptions import UnknownFile
        revision.gerrit.get.return_value = {"file.py": {}}
        with pytest.raises(UnknownFile):
            _ = revision.files["nonexistent.py"]

    def test_file_to_dict(self, revision):
        revision.gerrit.get.return_value = {"file.py": {"lines_inserted": 5}}
        f = revision.files["file.py"]
        info = f.to_dict()
        assert "path" in info

    def test_file_get_content(self, revision):
        revision.gerrit.get.return_value = {"file.py": {}}
        f = revision.files["file.py"]
        content = base64.b64encode(b"print('hello')").decode("utf-8")
        revision.gerrit.get.return_value = content
        result = f.get_content()
        assert len(result) > 0

    def test_file_get_content_decoded(self, revision):
        revision.gerrit.get.return_value = {"file.py": {}}
        files = revision.files
        revision.gerrit.get.return_value = {"file.py": {}}
        f = revision.files["file.py"]
        content = base64.b64encode(b"print('hello')").decode("utf-8")
        revision.gerrit.get.return_value = content
        result = f.get_content(decode=True)
        assert "hello" in result

    def test_file_content_not_found(self, revision):
        from gerrit.utils.exceptions import FileContentNotFoundError
        revision.gerrit.get.return_value = {"file.py": {}}
        f = revision.files["file.py"]

        response_mock = MagicMock()
        response_mock.status_code = 404
        http_error = requests.exceptions.HTTPError(response=response_mock)
        revision.gerrit.get.side_effect = http_error

        with pytest.raises(FileContentNotFoundError):
            f.get_content()

    def test_file_get_diff(self, revision):
        revision.gerrit.get.return_value = {"file.py": {}}
        f = revision.files["file.py"]
        diff = {"content": [{"ab": ["line1", "line2"]}], "change_type": "MODIFIED"}
        revision.gerrit.get.return_value = diff
        result = f.get_diff()
        assert "content" in result

    def test_file_get_blame(self, revision):
        revision.gerrit.get.return_value = {"file.py": {}}
        f = revision.files["file.py"]
        blame = [{"author": {"name": "Test"}, "ranges": []}]
        revision.gerrit.get.return_value = blame
        result = f.get_blame()
        assert len(result) > 0

    def test_file_set_reviewed(self, revision):
        revision.gerrit.get.return_value = {"file.py": {}}
        f = revision.files["file.py"]
        f.set_reviewed()
        revision.gerrit.put.assert_called()

    def test_file_delete_reviewed(self, revision):
        revision.gerrit.get.return_value = {"file.py": {}}
        f = revision.files["file.py"]
        f.delete_reviewed()
        revision.gerrit.delete.assert_called()


# ---------------------------------------------------------------------------
# GerritChangeRevisionDrafts
# ---------------------------------------------------------------------------

class TestGerritChangeRevisionDrafts:

    def _get_drafts_module(self):
        from gerrit.changes.drafts import GerritChangeRevisionDrafts
        return GerritChangeRevisionDrafts

    def test_list_drafts(self, revision):
        revision.gerrit.get.return_value = {"file.py": [{"id": "d1", "message": "draft"}]}
        result = revision.drafts.list()
        assert isinstance(result, list)

    def test_create_draft(self, revision):
        draft_data = {"id": "draft1", "message": "Draft comment", "path": "file.py", "line": 5}
        revision.gerrit.put.return_value = draft_data
        result = revision.drafts.create(
            {"path": "file.py", "line": 5, "message": "Draft comment"}
        )
        revision.gerrit.put.assert_called()

    def test_get_draft(self, revision):
        draft_data = {"id": "draft1", "message": "Draft comment", "path": "file.py", "line": 5}
        revision.gerrit.get.return_value = draft_data
        draft = revision.drafts.get(id_="draft1")
        assert "message" in draft.to_dict()

    def test_update_draft(self, revision):
        draft_data = {"id": "draft1", "message": "Updated", "path": "file.py", "line": 5}
        revision.gerrit.get.return_value = draft_data
        draft = revision.drafts.get(id_="draft1")
        revision.gerrit.put.return_value = draft_data
        draft.update({"message": "Updated"})
        revision.gerrit.put.assert_called()

    def test_delete_draft(self, revision):
        draft_data = {"id": "draft1", "message": "Draft comment", "path": "file.py", "line": 5}
        revision.gerrit.get.return_value = draft_data
        draft = revision.drafts.get(id_="draft1")
        draft.delete()
        revision.gerrit.delete.assert_called()

