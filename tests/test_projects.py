#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
"""
Unit tests for gerrit.projects — all HTTP calls are mocked.
"""
import logging
import pytest
import requests
from unittest.mock import MagicMock
from urllib.parse import quote_plus

from tests.conftest import PROJECT_DATA

logger = logging.getLogger(__name__)

BRANCH_DATA = {
    "ref": "refs/heads/master",
    "revision": "67ebf73496383c6777035e374d2d664009e2aa5c",
    "can_delete": False,
}

TAG_DATA = {
    "ref": "refs/tags/v1.0",
    "revision": "67ebf73496383c6777035e374d2d664009e2aa5c",
    "object": "abc123",
    "message": "v1.0 release",
}

COMMIT_DATA = {
    "commit": "1b16713d0ca30ecc9f6f3ac78554d57b5d4fa467",
    "author": {"name": "Test Author", "email": "author@example.com"},
    "committer": {"name": "Test Committer", "email": "committer@example.com"},
    "message": "Test commit message",
    "parents": [{"commit": "parent123"}],
    "subject": "Test commit message",
}


# ---------------------------------------------------------------------------
# GerritProjects (manager)
# ---------------------------------------------------------------------------

class TestGerritProjects:

    def test_list_projects(self, mock_gerrit):
        mock_gerrit.get.return_value = {"myProject": PROJECT_DATA}

        from gerrit.projects.projects import GerritProjects
        projects = GerritProjects(gerrit=mock_gerrit)
        result = projects.list(limit=25, skip=0)
        assert len(result) > 0

    def test_list_projects_with_state(self, mock_gerrit):
        mock_gerrit.get.return_value = {"myProject": PROJECT_DATA}

        from gerrit.projects.projects import GerritProjects
        projects = GerritProjects(gerrit=mock_gerrit)
        result = projects.list(limit=25, state="ACTIVE")
        assert isinstance(result, dict)

    def test_list_projects_all_and_state_raises(self, mock_gerrit):
        from gerrit.projects.projects import GerritProjects
        projects = GerritProjects(gerrit=mock_gerrit)
        with pytest.raises(ValueError):
            projects.list(is_all=True, state="ACTIVE")

    def test_list_projects_with_pattern(self, mock_gerrit):
        mock_gerrit.get.return_value = {"myProject": PROJECT_DATA}

        from gerrit.projects.projects import GerritProjects
        projects = GerritProjects(gerrit=mock_gerrit)
        result = projects.list(pattern_dispatcher={"prefix": "my"})
        assert isinstance(result, dict)

    def test_list_projects_with_branch(self, mock_gerrit):
        mock_gerrit.get.return_value = {"myProject": PROJECT_DATA}

        from gerrit.projects.projects import GerritProjects
        projects = GerritProjects(gerrit=mock_gerrit)
        result = projects.list(branch="master")
        assert isinstance(result, dict)

    def test_list_projects_is_all(self, mock_gerrit):
        mock_gerrit.get.return_value = {"myProject": PROJECT_DATA, "other": PROJECT_DATA}

        from gerrit.projects.projects import GerritProjects
        projects = GerritProjects(gerrit=mock_gerrit)
        result = projects.list(is_all=True)
        assert len(result) > 0

    def test_search_projects(self, mock_gerrit):
        mock_gerrit.get.return_value = [PROJECT_DATA]

        from gerrit.projects.projects import GerritProjects
        projects = GerritProjects(gerrit=mock_gerrit)
        result = projects.search(query="name:myProject")
        assert len(result) >= 1

    def test_get_project(self, mock_gerrit):
        mock_gerrit.get.return_value = PROJECT_DATA

        from gerrit.projects.projects import GerritProjects
        from gerrit.projects.project import GerritProject
        projects = GerritProjects(gerrit=mock_gerrit)
        project = projects.get(name="myProject")
        assert isinstance(project, GerritProject)
        assert project.name == PROJECT_DATA["name"]

    def test_get_project_not_found(self, mock_gerrit):
        response_mock = MagicMock()
        response_mock.status_code = 404
        http_error = requests.exceptions.HTTPError(response=response_mock)
        mock_gerrit.get.side_effect = http_error

        from gerrit.projects.projects import GerritProjects
        from gerrit.utils.exceptions import ProjectNotFoundError
        projects = GerritProjects(gerrit=mock_gerrit)
        with pytest.raises(ProjectNotFoundError):
            projects.get(name="nonexistent")

    def test_create_project(self, mock_gerrit):
        response_mock = MagicMock()
        response_mock.status_code = 404
        http_error = requests.exceptions.HTTPError(response=response_mock)
        # First get → 404 (not found), then put, then get again → project data × 2
        mock_gerrit.get.side_effect = [http_error, PROJECT_DATA, PROJECT_DATA]

        from gerrit.projects.projects import GerritProjects
        projects = GerritProjects(gerrit=mock_gerrit)
        result = projects.create("newProject", {"description": "New project"})
        assert result is not None
        mock_gerrit.put.assert_called_once()

    def test_create_project_already_exists(self, mock_gerrit):
        mock_gerrit.get.return_value = PROJECT_DATA

        from gerrit.projects.projects import GerritProjects
        from gerrit.utils.exceptions import ProjectAlreadyExistsError
        projects = GerritProjects(gerrit=mock_gerrit)
        with pytest.raises(ProjectAlreadyExistsError):
            projects.create("myProject", {})

    def test_delete_project(self, mock_gerrit):
        mock_gerrit.get.return_value = PROJECT_DATA

        from gerrit.projects.projects import GerritProjects
        projects = GerritProjects(gerrit=mock_gerrit)
        projects.delete("myProject")
        mock_gerrit.post.assert_called()


# ---------------------------------------------------------------------------
# GerritProject (single project)
# ---------------------------------------------------------------------------

class TestGerritProject:

    def test_project_str_and_repr(self, mock_project):
        assert str(mock_project) == PROJECT_DATA["id"]
        assert "GerritProject" in repr(mock_project)

    def test_project_attributes(self, mock_project):
        attrs = ["id", "name", "parent", "state", "labels", "web_links"]
        for attr in attrs:
            assert hasattr(mock_project, attr), f"Missing attribute: {attr}"

    def test_project_to_dict(self, mock_project):
        info = mock_project.to_dict()
        assert info.get("name") == PROJECT_DATA["name"]
        assert info.get("id") == PROJECT_DATA["id"]

    def test_project_equality(self, mock_project, mock_gerrit):
        """Two GerritProject objects with same endpoint should be equal."""
        mock_gerrit.get.return_value = PROJECT_DATA
        from gerrit.projects.project import GerritProject
        other = GerritProject(project_id=PROJECT_DATA["id"], gerrit=mock_gerrit)
        assert mock_project == other

    def test_project_inequality(self, mock_project, mock_gerrit):
        mock_gerrit.get.return_value = {**PROJECT_DATA, "id": "otherProject", "name": "otherProject"}
        from gerrit.projects.project import GerritProject
        other = GerritProject(project_id="otherProject", gerrit=mock_gerrit)
        assert mock_project != other

    def test_get_description(self, mock_project):
        mock_project.gerrit.get.return_value = "A test project"
        result = mock_project.get_description()
        assert result == "A test project"

    def test_set_description(self, mock_project):
        mock_project.gerrit.put.return_value = "Updated description"
        mock_project.set_description({"description": "Updated"})
        mock_project.gerrit.put.assert_called()

    def test_delete_description(self, mock_project):
        mock_project.delete_description()
        mock_project.gerrit.delete.assert_called()

    def test_delete_project(self, mock_project):
        mock_project.delete()
        mock_project.gerrit.post.assert_called()

    def test_get_parent(self, mock_project):
        mock_project.gerrit.get.return_value = "All-Projects"
        result = mock_project.get_parent()
        assert result == "All-Projects"

    def test_set_parent(self, mock_project):
        mock_project.gerrit.put.return_value = "New-Parent"
        mock_project.set_parent({"parent": "New-Parent"})
        mock_project.gerrit.put.assert_called()

    def test_get_head(self, mock_project):
        mock_project.gerrit.get.return_value = "refs/heads/master"
        result = mock_project.get_head()
        assert result == "refs/heads/master"

    def test_set_head(self, mock_project):
        mock_project.gerrit.put.return_value = "refs/heads/main"
        mock_project.set_head({"ref": "refs/heads/main"})
        mock_project.gerrit.put.assert_called()

    def test_get_access_rights(self, mock_project):
        access = {"inherits_from": {"name": "All-Projects"}, "local": {}}
        mock_project.gerrit.get.return_value = access
        result = mock_project.get_access_rights()
        assert "inherits_from" in result

    def test_set_access_rights(self, mock_project):
        mock_project.gerrit.post.return_value = {"inherits_from": {"name": "All-Projects"}}
        mock_project.set_access_rights({"add": {}, "remove": {}})
        mock_project.gerrit.post.assert_called()

    def test_child_projects(self, mock_project):
        mock_project.gerrit.get.return_value = [PROJECT_DATA]
        children = mock_project.child_projects
        assert len(children) >= 0

    def test_get_commit(self, mock_project):
        mock_project.gerrit.get.return_value = COMMIT_DATA
        from gerrit.projects.commit import GerritProjectCommit
        commit = mock_project.get_commit("1b16713d0ca30ecc9f6f3ac78554d57b5d4fa467")
        assert isinstance(commit, GerritProjectCommit)

    def test_get_commit_not_found(self, mock_project):
        response_mock = MagicMock()
        response_mock.status_code = 404
        http_error = requests.exceptions.HTTPError(response=response_mock)
        mock_project.gerrit.get.side_effect = http_error

        from gerrit.utils.exceptions import CommitNotFoundError
        with pytest.raises(CommitNotFoundError):
            mock_project.get_commit("0000000000")

    def test_get_config(self, mock_project):
        mock_project.gerrit.get.return_value = {"description": "test", "use_content_merge": "INHERIT"}
        result = mock_project.get_config()
        assert "description" in result

    def test_set_config(self, mock_project):
        mock_project.gerrit.put.return_value = {"description": "updated"}
        mock_project.set_config({"description": "updated"})
        mock_project.gerrit.put.assert_called()

    def test_run_gc(self, mock_project):
        mock_project.gerrit.post.return_value = {"status": "ok"}
        mock_project.run_garbage_collection({"show_progress": True})
        mock_project.gerrit.post.assert_called()


# ---------------------------------------------------------------------------
# GerritProjectBranches
# ---------------------------------------------------------------------------

class TestGerritProjectBranches:

    def test_list_branches(self, mock_project):
        mock_project.gerrit.get.return_value = [BRANCH_DATA]
        branches = mock_project.branches.list()
        assert len(branches) > 0

    def test_get_branch(self, mock_project):
        mock_project.gerrit.get.return_value = BRANCH_DATA
        from gerrit.projects.branches import GerritProjectBranch
        branch = mock_project.branches.get(name="master")
        assert isinstance(branch, GerritProjectBranch)
        assert branch.name == "master"

    def test_get_branch_not_found(self, mock_project):
        response_mock = MagicMock()
        response_mock.status_code = 404
        http_error = requests.exceptions.HTTPError(response=response_mock)
        mock_project.gerrit.get.side_effect = http_error

        from gerrit.utils.exceptions import BranchNotFoundError
        with pytest.raises(BranchNotFoundError):
            mock_project.branches.get(name="NONEXISTENT")

    def test_create_branch(self, mock_project):
        response_mock = MagicMock()
        response_mock.status_code = 404
        http_error = requests.exceptions.HTTPError(response=response_mock)
        mock_project.gerrit.get.side_effect = [http_error, BRANCH_DATA, BRANCH_DATA]

        from gerrit.projects.branches import GerritProjectBranch
        branch = mock_project.branches.create("new-branch", {"revision": "master"})
        assert isinstance(branch, GerritProjectBranch)

    def test_create_branch_already_exists(self, mock_project):
        mock_project.gerrit.get.return_value = BRANCH_DATA

        from gerrit.utils.exceptions import BranchAlreadyExistsError
        with pytest.raises(BranchAlreadyExistsError):
            mock_project.branches.create("master", {"revision": "abc123"})

    def test_delete_branch(self, mock_project):
        mock_project.gerrit.get.return_value = BRANCH_DATA
        mock_project.branches.delete("master")
        mock_project.gerrit.delete.assert_called()

    def test_branch_to_dict(self, mock_project):
        mock_project.gerrit.get.return_value = BRANCH_DATA
        branch = mock_project.branches.get(name="master")
        info = branch.to_dict()
        assert info.get("ref") == BRANCH_DATA["ref"]

    def test_branch_str(self, mock_project):
        mock_project.gerrit.get.return_value = BRANCH_DATA
        branch = mock_project.branches.get(name="master")
        assert str(branch) == "master"

    def test_branch_get_file_content(self, mock_project):
        import base64
        content = base64.b64encode(b"file content").decode("utf-8")
        mock_project.gerrit.get.side_effect = [BRANCH_DATA, BRANCH_DATA, content, content]
        branch = mock_project.branches.get(name="master")
        result = branch.get_file_content("README.md")
        assert len(result) > 0

        result_decoded = branch.get_file_content("README.md", decode=True)
        assert len(result_decoded) > 0

    def test_branch_get_reflog(self, mock_project):
        mock_project.gerrit.get.return_value = BRANCH_DATA
        branch = mock_project.branches.get(name="master")
        mock_project.gerrit.get.return_value = [{"old_id": "abc", "new_id": "def"}]
        result = branch.get_reflog()
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# GerritProjectTags
# ---------------------------------------------------------------------------

class TestGerritProjectTags:

    def test_list_tags(self, mock_project):
        mock_project.gerrit.get.return_value = [TAG_DATA]
        tags = mock_project.tags.list()
        assert len(tags) > 0

    def test_get_tag(self, mock_project):
        mock_project.gerrit.get.return_value = TAG_DATA
        from gerrit.projects.tags import GerritProjectTag
        tag = mock_project.tags.get(name="v1.0")
        assert isinstance(tag, GerritProjectTag)
        assert tag.name == "v1.0"

    def test_get_tag_not_found(self, mock_project):
        response_mock = MagicMock()
        response_mock.status_code = 404
        http_error = requests.exceptions.HTTPError(response=response_mock)
        mock_project.gerrit.get.side_effect = http_error

        from gerrit.utils.exceptions import TagNotFoundError
        with pytest.raises(TagNotFoundError):
            mock_project.tags.get(name="NONEXISTENT")

    def test_create_tag(self, mock_project):
        response_mock = MagicMock()
        response_mock.status_code = 404
        http_error = requests.exceptions.HTTPError(response=response_mock)
        mock_project.gerrit.get.side_effect = [http_error, TAG_DATA, TAG_DATA]

        from gerrit.projects.tags import GerritProjectTag
        tag = mock_project.tags.create("v2.0", {"revision": "abc123"})
        assert isinstance(tag, GerritProjectTag)

    def test_create_tag_already_exists(self, mock_project):
        mock_project.gerrit.get.return_value = TAG_DATA

        from gerrit.utils.exceptions import TagAlreadyExistsError
        with pytest.raises(TagAlreadyExistsError):
            mock_project.tags.create("v1.0", {"revision": "abc123"})

    def test_delete_tag(self, mock_project):
        mock_project.gerrit.get.return_value = TAG_DATA
        mock_project.tags.delete("v1.0")
        mock_project.gerrit.delete.assert_called()

    def test_tag_to_dict(self, mock_project):
        mock_project.gerrit.get.return_value = TAG_DATA
        tag = mock_project.tags.get(name="v1.0")
        info = tag.to_dict()
        assert info.get("ref") == TAG_DATA["ref"]

    def test_tag_str(self, mock_project):
        mock_project.gerrit.get.return_value = TAG_DATA
        tag = mock_project.tags.get(name="v1.0")
        assert str(tag) == "v1.0"


# ---------------------------------------------------------------------------
# GerritProjectCommit
# ---------------------------------------------------------------------------

class TestGerritProjectCommit:

    def _get_commit(self, mock_project):
        mock_project.gerrit.get.return_value = COMMIT_DATA
        return mock_project.get_commit("1b16713d0ca30ecc9f6f3ac78554d57b5d4fa467")

    def test_commit_str(self, mock_project):
        commit = self._get_commit(mock_project)
        assert str(commit) == "1b16713d0ca30ecc9f6f3ac78554d57b5d4fa467"

    def test_commit_to_dict(self, mock_project):
        commit = self._get_commit(mock_project)
        detail = commit.to_dict()
        assert "author" in detail
        assert "commit" in detail
        assert "message" in detail

    def test_commit_get_include_in(self, mock_project):
        commit = self._get_commit(mock_project)
        mock_project.gerrit.get.return_value = {"branches": ["master"], "tags": ["v1.0"]}
        result = commit.get_include_in()
        assert "branches" in result
        assert "tags" in result

    def test_commit_get_file_content(self, mock_project):
        import base64
        content = base64.b64encode(b"hello world").decode("utf-8")
        commit = self._get_commit(mock_project)
        mock_project.gerrit.get.return_value = content
        result = commit.get_file_content("README.md")
        assert len(result) > 0

        result_decoded = commit.get_file_content("README.md", decode=True)
        assert len(result_decoded) > 0

    def test_commit_list_change_files(self, mock_project):
        commit = self._get_commit(mock_project)
        mock_project.gerrit.get.return_value = {"README.md": {}, "src/main.py": {}}
        files = commit.list_change_files()
        assert "README.md" in files  # files is a dict


# ---------------------------------------------------------------------------
# GerritProjectDashboards and Labels
# ---------------------------------------------------------------------------

class TestGerritProjectDashboardsAndLabels:

    def test_list_dashboards(self, mock_project):
        mock_project.gerrit.get.return_value = []
        dashboards = mock_project.dashboards.list()
        assert len(dashboards) >= 0

    def test_list_labels(self, mock_project):
        mock_project.gerrit.get.return_value = []
        labels = mock_project.labels.list()
        assert len(labels) >= 0

