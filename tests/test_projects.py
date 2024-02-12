#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import logging
import pytest
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


@pytest.fixture()
def gerrit_object(request):
    param = request.param
    return param


data = [
    {
        "project_name": "LineageOS/android",
        "branch": "lineage-20.0",
        "tag": "cm-10.2-M1",
        "file": "default.xml",
    },
    {
        "project_name": "LineageOS/Superuser",
        "branch": "master",
        "tag": "cm-10.2.1",
        "file": "README.md",
    },
]


@pytest.mark.parametrize('is_all, limit, skip, pattern_dispatcher, project_type, description, branch, state',
                         [(False, 25, 0, None, None, False, None, "ACTIVE"),
                          (False, 25, 25, None, None, False, None, "ACTIVE"),
                          (True, 25, 0, None, None, False, None, None),
                          (False, 25, 0, {"prefix": "Lineage"}, None, False, None, None),
                          (False, 25, 0, None, "all", False, None, None),
                          (False, 25, 0, None, None, True, None, None),
                          (False, 25, 0, None, None, False, "master", None),
                          ])
def test_list_projects(gerrit_client, is_all, limit, skip, pattern_dispatcher, project_type, description, branch, state):
    resp = gerrit_client.projects.list(is_all, limit, skip, pattern_dispatcher, project_type, description, branch, state)

    assert len(resp) > 0


def test_list_all_project(gerrit_client):
    with pytest.raises(ValueError):
        gerrit_client.projects.list(is_all=True, state="ACTIVE")

    resp = gerrit_client.projects.list(is_all=True)

    assert len(resp) > 25


@pytest.mark.parametrize('query', ["name:LineageOS/android", "inname:LineageOS",
                                   "state:read-only", "parent:Head-Developers"])
def test_search_projects(gerrit_client, query):
    resp = gerrit_client.projects.search(query=query)

    assert len(resp) >= 1


@pytest.mark.parametrize('gerrit_object', data, indirect=True)
def test_get_project(gerrit_client, gerrit_object):
    from gerrit.projects.project import GerritProject
    from gerrit.utils.exceptions import ProjectNotFoundError
    with pytest.raises(ProjectNotFoundError):
        gerrit_client.projects.get(name="test-project0000000")

    project_name = gerrit_object["project_name"]
    project = gerrit_client.projects.get(name=project_name)
    logger.debug(project.to_dict())

    assert isinstance(project, GerritProject)

    attrs = ["id", "name", "parent", "state", "labels", "web_links"]
    for attr in attrs:
        logger.debug(f"{attr}, {hasattr(project, attr)}, {getattr(project, attr)}")

    assert all([hasattr(project, attr) for attr in attrs])

    project_id = project.id
    assert str(project) == f"{project_id}"
    assert repr(project) == f"<gerrit.projects.project.GerritProject {project_id}>"

    project_info = project.to_dict()
    assert project_info.get("name") == project_name
    assert project_info.get("id") == quote_plus(project_name)

    assert project.name == project_name

    assert project != gerrit_client.projects.get(name="LineageOS/android_art")
    assert project != gerrit_client.accounts.get(account="jialiang.shi")


@pytest.mark.parametrize('gerrit_object', data, indirect=True)
def test_get_project_access_rights(gerrit_client, gerrit_object):
    project_name = gerrit_object["project_name"]
    project = gerrit_client.projects.get(name=project_name)
    access_rights = project.get_access_rights()
    assert "inherits_from" in access_rights.keys()


@pytest.mark.parametrize('project_name, expected',
                         [("LineageOS/android", "Head-Developers"),
                          ("LineageOS/android_device_google_tangorpro", "PROJECT-Google-tangorpro")
                          ])
def test_get_project_parent(gerrit_client, project_name, expected):
    project = gerrit_client.projects.get(name=project_name)
    HEAD = project.get_parent()
    assert HEAD == expected


@pytest.mark.parametrize('project_name, expected',
                         [("LineageOS/android", "refs/heads/master")])
def test_get_project_head(gerrit_client, project_name, expected):
    project = gerrit_client.projects.get(name=project_name)
    HEAD = project.get_head()
    assert HEAD == expected


@pytest.mark.xfail(reason="Request is not authorized")
def test_set_project_description(gerrit_client):
    input_ = {
        "description": "Git Repo Project",
        "commit_message": "Update the project description"
    }
    project_name = "LineageOS/android"  # "git-repo"
    project = gerrit_client.projects.get(project_name)
    project.set_description(input_)


@pytest.mark.xfail(reason="Request is not authorized")
def test_delete_project_description(gerrit_client):
    project_name = "LineageOS/android"  # "git-repo"
    project = gerrit_client.projects.get(project_name)
    project.delete_description()


@pytest.mark.xfail(reason="Request is not authorized")
def test_create_project(gerrit_client):
    from gerrit.utils.exceptions import ProjectAlreadyExistsError
    input_ = {
        "description": "This is a demo project.",
        "submit_type": "INHERIT",
        "owners": [
            "MyProject-Owners"
        ]
    }
    project_name = "LineageOS/android"  # "git-repo"
    with pytest.raises(ProjectAlreadyExistsError):
        gerrit_client.projects.create(project_name, input_)

    project = gerrit_client.projects.create('MyProject', input_)
    assert project.name == "MyProject"


@pytest.mark.xfail(reason="Request is not authorized")
def test_delete_project(gerrit_client):
    project_name = "LineageOS/android"  # "git-repo"
    gerrit_client.projects.delete(project_name)

    project = gerrit_client.projects.get(project_name)
    project.delete()


def test_get_child_projects(gerrit_client):
    project_name = "Head-Developers"
    project = gerrit_client.projects.get(name=project_name)
    children = project.child_projects

    assert len(children) >= 0


@pytest.mark.parametrize('gerrit_object', data, indirect=True)
def test_project_branches(gerrit_client, gerrit_object):
    project_name = gerrit_object["project_name"]
    project = gerrit_client.projects.get(name=project_name)
    branches = project.branches.list()
    assert len(branches) > 0

    from gerrit.utils.exceptions import BranchNotFoundError
    with pytest.raises(BranchNotFoundError):
        project.branches.get(name="TEST-BRANCH")

    branch_name = gerrit_object["branch"]
    branch = project.branches.get(name=branch_name)
    assert branch.name == branch_name
    assert str(branch) == f"{branch_name}"

    master_info = branch.to_dict()
    assert master_info.get("ref") == f"refs/heads/{branch_name}"

    file_name = gerrit_object["file"]
    file = branch.get_file_content(file=file_name)
    assert len(file) > 0

    file = branch.get_file_content(file=file_name, decode=True)
    assert len(file) > 0


def test_project_branch_is_mergeable(gerrit_client):
    project_name = "LineageOS/android"  # "git-repo"
    project = gerrit_client.projects.get(name=project_name)
    branch_name = "lineage-20.0"
    branch = project.branches.get(name=branch_name)
    input_ = {
        'source': 'lineage-19.1',
        'strategy': 'recursive'
    }
    res = branch.is_mergeable(input_)
    assert "mergeable" in res.keys()

    from gerrit.utils.exceptions import BranchNotFoundError
    with pytest.raises(BranchNotFoundError):
        input_ = {
            'source': 'lineage-19.2',
            'strategy': 'recursive'
        }
        branch.is_mergeable(input_)


@pytest.mark.xfail(reason="Request is not authorized")
def test_create_project_branch(gerrit_client):
    from gerrit.utils.exceptions import BranchAlreadyExistsError
    input_ = {
        'revision': '1b16713d0ca30ecc9f6f3ac78554d57b5d4fa467'
    }
    project_name = "LineageOS/android"  # "git-repo"
    project = gerrit_client.projects.get(project_name)

    with pytest.raises(BranchAlreadyExistsError):
        project.branches.create('lineage-20.0', input_)

    new_branch = project.branches.create('stable', input_)
    assert new_branch.name == "stable"


@pytest.mark.xfail(reason="Request is not authorized")
def test_delete_project_branch(gerrit_client):
    project_name = "LineageOS/android"  # "git-repo"
    project = gerrit_client.projects.get(project_name)
    project.branches.delete("lineage-20.0")


@pytest.mark.parametrize('gerrit_object', data, indirect=True)
def test_project_tags(gerrit_client, gerrit_object):
    project_name = gerrit_object["project_name"]
    project = gerrit_client.projects.get(name=project_name)
    tags = project.tags.list()
    assert len(tags) > 0

    from gerrit.utils.exceptions import TagNotFoundError
    with pytest.raises(TagNotFoundError):
        project.tags.get(name="TEST-TAG")

    tag_name = gerrit_object["tag"]
    tag = project.tags.get(name=tag_name)
    assert tag.name == tag_name
    assert str(tag) == f"{tag_name}"

    tag_info = tag.to_dict()
    assert tag_info.get("ref") == f"refs/tags/{tag_name}"


@pytest.mark.xfail(reason="Request is not authorized")
def test_create_project_tag(gerrit_client):
    from gerrit.utils.exceptions import TagAlreadyExistsError
    input_ = {
        "message": "annotation",
        'revision': '8351e4f8077fa038ea3ecbf60925581c8c40ccc4'
    }
    project_name = "LineageOS/android"  # "git-repo"
    project = gerrit_client.projects.get(project_name)

    with pytest.raises(TagAlreadyExistsError):
        project.tags.create('cm-10.2-M1', input_)

    new_branch = project.tags.create('cm-10.2', input_)
    assert new_branch.name == "cm-10.2"


@pytest.mark.xfail(reason="Request is not authorized")
def test_delete_project_tag(gerrit_client):
    project_name = "LineageOS/android"  # "git-repo"
    project = gerrit_client.projects.get(project_name)
    project.tags.delete("cm-10.2-M1")


def test_get_project_commit(gerrit_client):
    project_name = "LineageOS/android"  # "git-repo"
    project = gerrit_client.projects.get(name=project_name)

    hash_ = "1b16713d0ca30ecc9f6f3ac78554d57b5d4fa467"
    commit = project.get_commit(hash_)

    from gerrit.utils.exceptions import CommitNotFoundError
    with pytest.raises(CommitNotFoundError):
        project.get_commit(commit="00000000000000000000")

    assert str(commit) == f"{hash_}"

    detail = commit.to_dict()
    assert "author" in detail
    assert "commit" in detail
    assert "message" in detail
    assert "parents" in detail
    assert "subject" in detail

    include_in = commit.get_include_in()
    assert "branches" in include_in
    assert "tags" in include_in

    file_name = "default.xml"
    content = commit.get_file_content(file_name)
    assert len(content) > 0

    content = commit.get_file_content(file_name, decode=True)
    assert len(content) > 0

    assert file_name in commit.list_change_files()


@pytest.mark.xfail(reason="Request is not authorized")
def test_get_project_labels(gerrit_client):
    project_name = "LineageOS/android_frameworks_base"
    project = gerrit_client.projects.get(name=project_name)

    labels = project.labels.list()
    assert len(labels) >= 0


def test_get_project_dashboards(gerrit_client):
    project_name = "LineageOS/android_frameworks_base"
    project = gerrit_client.projects.get(name=project_name)

    dashboards = project.dashboards.list()
    assert len(dashboards) >= 0
