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
        # put() succeeds; get() is called twice (projects.get → gerrit.get + GerritProject.poll)
        mock_gerrit.get.side_effect = [PROJECT_DATA, PROJECT_DATA]

        from gerrit.projects.projects import GerritProjects
        projects = GerritProjects(gerrit=mock_gerrit)
        result = projects.create("newProject", {"description": "New project"})
        assert result is not None
        mock_gerrit.put.assert_called_once()

    def test_create_project_already_exists(self, mock_gerrit):
        from gerrit.projects.projects import GerritProjects
        from gerrit.utils.exceptions import ConflictError, ProjectAlreadyExistsError
        mock_gerrit.put.side_effect = ConflictError("409 Conflict: Project already exists")

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

    def test_get_child_project(self, mock_project):
        mock_project.gerrit.get.return_value = PROJECT_DATA
        result = mock_project.get_child_project("childProject")
        mock_project.gerrit.get.assert_called()
        assert result is not None

    def test_get_child_project_recursive(self, mock_project):
        mock_project.gerrit.get.return_value = PROJECT_DATA
        result = mock_project.get_child_project("childProject", recursive=True)
        call_args = mock_project.gerrit.get.call_args
        assert call_args[1].get("params", {}).get("recursive") == 1
        assert result is not None

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
        # put() succeeds; branches.get() calls gerrit.get() twice (get + poll)
        mock_project.gerrit.get.side_effect = [BRANCH_DATA, BRANCH_DATA]

        from gerrit.projects.branches import GerritProjectBranch
        branch = mock_project.branches.create("new-branch", {"revision": "master"})
        assert isinstance(branch, GerritProjectBranch)

    def test_create_branch_already_exists(self, mock_project):
        from gerrit.utils.exceptions import ConflictError, BranchAlreadyExistsError
        mock_project.gerrit.put.side_effect = ConflictError("409 Conflict: Branch already exists")

        with pytest.raises(BranchAlreadyExistsError):
            mock_project.branches.create("master", {"revision": "abc123"})

    def test_delete_branch(self, mock_project):
        mock_project.gerrit.get.return_value = BRANCH_DATA
        mock_project.branches.delete("master")
        mock_project.gerrit.delete.assert_called()

    def test_delete_branches(self, mock_project):
        input_ = {"branches": ["stable-1.0", "stable-2.0"]}
        mock_project.branches.delete_branches(input_)
        mock_project.gerrit.post.assert_called_once()
        call_args = mock_project.gerrit.post.call_args
        assert ":delete" in call_args[0][0]
        assert call_args[1]["json"] == input_

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
        # put() succeeds; tags.get() calls gerrit.get() twice (get + poll)
        mock_project.gerrit.get.side_effect = [TAG_DATA, TAG_DATA]

        from gerrit.projects.tags import GerritProjectTag
        tag = mock_project.tags.create("v2.0", {"revision": "abc123"})
        assert isinstance(tag, GerritProjectTag)

    def test_create_tag_already_exists(self, mock_project):
        from gerrit.utils.exceptions import ConflictError, TagAlreadyExistsError
        mock_project.gerrit.put.side_effect = ConflictError("409 Conflict: Tag already exists")

        with pytest.raises(TagAlreadyExistsError):
            mock_project.tags.create("v1.0", {"revision": "abc123"})

    def test_delete_tag(self, mock_project):
        mock_project.gerrit.get.return_value = TAG_DATA
        mock_project.tags.delete("v1.0")
        mock_project.gerrit.delete.assert_called()

    def test_delete_tags(self, mock_project):
        input_ = {"tags": ["v1.0", "v2.0"]}
        mock_project.tags.delete_tags(input_)
        mock_project.gerrit.post.assert_called_once()
        call_args = mock_project.gerrit.post.call_args
        assert ":delete" in call_args[0][0]
        assert call_args[1]["json"] == input_

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

    def test_get_dashboard(self, mock_project):
        dashboard_data = {"id": "master:closed", "project": "myProject", "title": "Closed Changes"}
        mock_project.gerrit.get.return_value = dashboard_data
        from gerrit.projects.dashboards import GerritProjectDashboard
        dashboard = mock_project.dashboards.get("master:closed")
        assert isinstance(dashboard, GerritProjectDashboard)

    def test_set_dashboard(self, mock_project):
        dashboard_data = {"id": "master:closed", "project": "myProject", "title": "Closed Changes"}
        mock_project.gerrit.get.return_value = dashboard_data
        from gerrit.projects.dashboards import GerritProjectDashboard
        dashboard = mock_project.dashboards.get("master:closed")
        mock_project.gerrit.put.return_value = dashboard_data
        dashboard.set({"id": "master:closed", "commit_message": "Update dashboard"})
        mock_project.gerrit.put.assert_called()

    def test_list_labels(self, mock_project):
        mock_project.gerrit.get.return_value = []
        labels = mock_project.labels.list()
        assert len(labels) >= 0


# ---------------------------------------------------------------------------
# GerritProjectSubmitRequirements
# ---------------------------------------------------------------------------

SR_DATA = {
    "name": "Code-Review",
    "description": "At least one maximum vote for label 'Code-Review' is required",
    "submittability_expression": "label:Code-Review=MAX,user=non_uploader",
    "allow_override_in_child_projects": True,
}


class TestGerritProjectSubmitRequirements:

    def test_list_submit_requirements(self, mock_project):
        mock_project.gerrit.get.return_value = [SR_DATA]
        srs = mock_project.submit_requirements.list()
        assert len(srs) >= 1

    def test_get_submit_requirement(self, mock_project):
        mock_project.gerrit.get.return_value = SR_DATA
        from gerrit.projects.submit_requirements import GerritProjectSubmitRequirement
        sr = mock_project.submit_requirements.get("Code-Review")
        assert isinstance(sr, GerritProjectSubmitRequirement)
        assert sr.name == SR_DATA["name"]

    def test_create_submit_requirement(self, mock_project):
        mock_project.gerrit.put.return_value = SR_DATA
        result = mock_project.submit_requirements.create(
            "Code-Review",
            {
                "submittability_expression": "label:Code-Review=MAX,user=non_uploader",
                "allow_override_in_child_projects": True,
            },
        )
        mock_project.gerrit.put.assert_called_once()
        call_args = mock_project.gerrit.put.call_args
        assert "Code-Review" in call_args[0][0]

    def test_delete_submit_requirement(self, mock_project):
        mock_project.submit_requirements.delete("Code-Review")
        mock_project.gerrit.delete.assert_called_once()
        call_args = mock_project.gerrit.delete.call_args
        assert "Code-Review" in call_args[0][0]

    def test_submit_requirement_update(self, mock_project):
        mock_project.gerrit.get.return_value = SR_DATA
        from gerrit.projects.submit_requirements import GerritProjectSubmitRequirement
        sr = mock_project.submit_requirements.get("Code-Review")
        updated = {**SR_DATA, "allow_override_in_child_projects": False}
        mock_project.gerrit.post.return_value = updated
        result = sr.update({"allow_override_in_child_projects": False})
        mock_project.gerrit.post.assert_called()
        call_args = mock_project.gerrit.post.call_args
        assert "Code-Review" in call_args[0][0]

    def test_submit_requirement_delete(self, mock_project):
        mock_project.gerrit.get.return_value = SR_DATA
        sr = mock_project.submit_requirements.get("Code-Review")
        sr.delete()
        mock_project.gerrit.delete.assert_called()

    def test_submit_requirements_property_type(self, mock_project):
        from gerrit.projects.submit_requirements import GerritProjectSubmitRequirements
        assert isinstance(mock_project.submit_requirements, GerritProjectSubmitRequirements)


# ---------------------------------------------------------------------------
# GerritProjectWebHooks
# ---------------------------------------------------------------------------

WEBHOOK_DATA = {
    "name": "my-webhook",
    "url": "https://example.com/gerrit-events",
    "maxTries": "3",
    "sslVerify": "true",
}


class TestGerritProjectWebhooks:

    def test_list_webhooks(self, mock_project):
        mock_project.gerrit.get.return_value = [WEBHOOK_DATA]
        from gerrit.projects.webhooks import GerritProjectWebHooks
        webhooks = GerritProjectWebHooks(project=mock_project.id, gerrit=mock_project.gerrit)
        result = webhooks.list()
        assert len(result) >= 1

    def test_create_webhook(self, mock_project):
        mock_project.gerrit.put.return_value = WEBHOOK_DATA
        from gerrit.projects.webhooks import GerritProjectWebHooks
        webhooks = GerritProjectWebHooks(project=mock_project.id, gerrit=mock_project.gerrit)
        result = webhooks.create("my-webhook", WEBHOOK_DATA)
        mock_project.gerrit.put.assert_called_once()

    def test_get_webhook(self, mock_project):
        mock_project.gerrit.get.return_value = WEBHOOK_DATA
        from gerrit.projects.webhooks import GerritProjectWebHooks, GerritProjectWebHook
        webhooks = GerritProjectWebHooks(project=mock_project.id, gerrit=mock_project.gerrit)
        webhook = webhooks.get("my-webhook")
        assert isinstance(webhook, GerritProjectWebHook)
        assert str(webhook) == "my-webhook"

    def test_delete_webhook_via_manager(self, mock_project):
        from gerrit.projects.webhooks import GerritProjectWebHooks
        webhooks = GerritProjectWebHooks(project=mock_project.id, gerrit=mock_project.gerrit)
        webhooks.delete("my-webhook")
        mock_project.gerrit.delete.assert_called_once()

    def test_delete_webhook_via_instance(self, mock_project):
        mock_project.gerrit.get.return_value = WEBHOOK_DATA
        from gerrit.projects.webhooks import GerritProjectWebHooks, GerritProjectWebHook
        webhooks = GerritProjectWebHooks(project=mock_project.id, gerrit=mock_project.gerrit)
        webhook = webhooks.get("my-webhook")
        webhook.delete()
        mock_project.gerrit.delete.assert_called()

    def test_webhooks_property_on_project(self, mock_project):
        from gerrit.projects.webhooks import GerritProjectWebHooks
        assert isinstance(mock_project.webhooks, GerritProjectWebHooks)


# ---------------------------------------------------------------------------
# GerritProjectLabels
# ---------------------------------------------------------------------------

LABEL_DATA = {
    "name": "Code-Review",
    "project_name": "myProject",
    "function": "MaxWithBlock",
    "values": {" 0": "No score", "+1": "LGTM", "+2": "Approved", "-1": "Not LGTM", "-2": "Reject"},
    "default_value": 0,
}


class TestGerritProjectLabels:

    def test_list_labels(self, mock_project):
        mock_project.gerrit.get.return_value = [LABEL_DATA]
        result = mock_project.labels.list()
        assert len(result) >= 1

    def test_get_label(self, mock_project):
        mock_project.gerrit.get.return_value = LABEL_DATA
        from gerrit.projects.labels import GerritProjectLabel
        label = mock_project.labels.get("Code-Review")
        assert isinstance(label, GerritProjectLabel)
        assert str(label) == "Code-Review"

    def test_create_label(self, mock_project):
        mock_project.gerrit.put.return_value = LABEL_DATA
        result = mock_project.labels.create(
            "Code-Review",
            {"values": {" 0": "No score", "+1": "LGTM"}, "commit_message": "Create label"},
        )
        mock_project.gerrit.put.assert_called_once()

    def test_delete_label_via_manager(self, mock_project):
        mock_project.labels.delete("Code-Review")
        mock_project.gerrit.delete.assert_called_once()

    def test_set_label(self, mock_project):
        mock_project.gerrit.get.return_value = LABEL_DATA
        from gerrit.projects.labels import GerritProjectLabel
        label = mock_project.labels.get("Code-Review")
        mock_project.gerrit.put.return_value = LABEL_DATA
        result = label.set({"commit_message": "Update label"})
        mock_project.gerrit.put.assert_called()

    def test_delete_label_via_instance(self, mock_project):
        mock_project.gerrit.get.return_value = LABEL_DATA
        from gerrit.projects.labels import GerritProjectLabel
        label = mock_project.labels.get("Code-Review")
        label.delete()
        mock_project.gerrit.delete.assert_called()


# ---------------------------------------------------------------------------
# GerritProjectDashboards – additional coverage
# ---------------------------------------------------------------------------

class TestGerritProjectDashboardsExtra:

    def test_create_dashboard(self, mock_project):
        dashboard_data = {"id": "master:closed", "project": "myProject", "title": "Closed"}
        mock_project.gerrit.put.return_value = dashboard_data
        result = mock_project.dashboards.create(
            "master:closed",
            {"id": "master:closed", "commit_message": "Define default dashboard"},
        )
        mock_project.gerrit.put.assert_called_once()

    def test_delete_dashboard_via_manager(self, mock_project):
        mock_project.dashboards.delete("master:closed")
        mock_project.gerrit.delete.assert_called_once()

    def test_delete_dashboard_via_instance(self, mock_project):
        dashboard_data = {"id": "master:closed", "project": "myProject", "title": "Closed"}
        mock_project.gerrit.get.return_value = dashboard_data
        from gerrit.projects.dashboards import GerritProjectDashboard
        dashboard = mock_project.dashboards.get("master:closed")
        assert str(dashboard) == "master:closed"
        dashboard.delete()
        mock_project.gerrit.delete.assert_called()


# ---------------------------------------------------------------------------
# GerritProjectBranch – additional coverage
# ---------------------------------------------------------------------------

class TestGerritProjectBranchExtra:

    def test_branch_delete(self, mock_project):
        from gerrit.projects.branches import GerritProjectBranch
        branch = GerritProjectBranch(
            name="master", project=mock_project.id, gerrit=mock_project.gerrit
        )
        mock_project.gerrit.get.return_value = {
            "ref": "refs/heads/master", "revision": "abc", "can_delete": False
        }
        branch.delete()
        mock_project.gerrit.delete.assert_called()

    def test_branch_is_mergeable(self, mock_project):
        from gerrit.projects.branches import GerritProjectBranch

        branch = GerritProjectBranch(
            name="master", project=mock_project.id, gerrit=mock_project.gerrit
        )

        # projects.get → mock_project (already exists)
        mock_branch = MagicMock()
        mock_project_obj = MagicMock()
        mock_project_obj.branches.get.return_value = mock_branch
        mock_project.gerrit.projects.get.return_value = mock_project_obj

        mock_project.gerrit.get.return_value = {"mergeable": True}
        result = branch.is_mergeable({"source": "stable", "strategy": "recursive"})
        assert result["mergeable"] is True

    def test_branch_get_non_404_error_raises(self, mock_project):
        from gerrit.utils.exceptions import GerritAPIException
        import requests

        response_mock = MagicMock()
        response_mock.status_code = 500
        mock_project.gerrit.get.side_effect = requests.exceptions.HTTPError(
            response=response_mock
        )
        with pytest.raises(GerritAPIException):
            mock_project.branches.get("master")


# ---------------------------------------------------------------------------
# GerritProject additional methods
# ---------------------------------------------------------------------------

class TestGerritProjectExtra:

    def test_get_statistics(self, mock_project):
        mock_project.gerrit.get.return_value = {"number_of_loose_objects": 0}
        result = mock_project.get_statistics()
        mock_project.gerrit.get.assert_called()

    def test_set_config(self, mock_project):
        mock_project.gerrit.put.return_value = {}
        result = mock_project.set_config({"description": "new desc"})
        mock_project.gerrit.put.assert_called()

    def test_create_change(self, mock_project):
        mock_project.gerrit.post.return_value = {"id": "change1"}
        result = mock_project.create_change({"subject": "test"})
        mock_project.gerrit.post.assert_called()

    def test_set_access_rights_for_review(self, mock_project):
        mock_project.gerrit.put.return_value = {}
        result = mock_project.create_access_rights_change({})
        mock_project.gerrit.put.assert_called()

    def test_check_access(self, mock_project):
        mock_project.gerrit.get.return_value = {"status": 200}
        result = mock_project.check_access("account=admin&ref=refs/heads/master")
        mock_project.gerrit.get.assert_called()

    def test_index_all_changes(self, mock_project):
        mock_project.index_all_changes()
        mock_project.gerrit.post.assert_called()

    def test_ban_commits(self, mock_project):
        mock_project.gerrit.put.return_value = {}
        result = mock_project.ban_commits({"commits": ["abc123"]})
        mock_project.gerrit.put.assert_called()
