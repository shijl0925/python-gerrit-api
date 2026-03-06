#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import pytest
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# Sample data used across tests
# ---------------------------------------------------------------------------

CHANGE_DATA = {
    "id": "myProject~master~I8473b95934b5732ac55d26311a706c9c2bde9940",
    "project": "myProject",
    "branch": "master",
    "hashtags": [],
    "change_id": "I8473b95934b5732ac55d26311a706c9c2bde9940",
    "subject": "Test change",
    "status": "NEW",
    "created": "2013-02-01 09:59:32.126000000",
    "updated": "2013-02-21 11:16:36.775000000",
    "_number": 1234,
    "owner": {"_account_id": 1000096},
    "insertions": 1,
    "deletions": 2,
}

ACCOUNT_DATA = {
    "_account_id": 1000096,
    "name": "Test User",
    "email": "test@example.com",
    "username": "testuser",
    "avatars": [{"url": "https://example.com/avatar.png", "height": 32}],
}

PROJECT_DATA = {
    "id": "myProject",
    "name": "myProject",
    "parent": "All-Projects",
    "state": "ACTIVE",
    "labels": {},
    "web_links": [],
}

GROUP_DATA = {
    "id": "6a1e70e1a88782771a91808c8af9bbb7a9871389",
    "name": "MyGroup",
    "description": "Test group",
    "group_id": 613,
    "owner": "MyGroup",
    "owner_id": "6a1e70e1a88782771a91808c8af9bbb7a9871389",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_gerrit():
    """
    Return a MagicMock that behaves like GerritClient.
    Tests configure ``mock_gerrit.get.return_value`` / ``side_effect`` as needed.
    """
    from gerrit import GerritClient

    gerrit = MagicMock(spec=GerritClient)
    gerrit.default_headers = {"Content-Type": "application/json; charset=UTF-8"}
    # Provide sensible defaults so object constructors don't fail
    gerrit.get.return_value = {}
    gerrit.post.return_value = {}
    gerrit.put.return_value = {}
    gerrit.delete.return_value = None
    return gerrit


@pytest.fixture
def mock_change(mock_gerrit):
    """Return a pre-initialised GerritChange backed by mock_gerrit."""
    from gerrit.changes.change import GerritChange

    mock_gerrit.get.return_value = CHANGE_DATA
    change = GerritChange(
        id=CHANGE_DATA["id"],
        gerrit=mock_gerrit,
    )
    return change


@pytest.fixture
def mock_account(mock_gerrit):
    """Return a pre-initialised GerritAccount backed by mock_gerrit."""
    from gerrit.accounts.account import GerritAccount

    mock_gerrit.get.return_value = ACCOUNT_DATA
    account = GerritAccount(
        account=ACCOUNT_DATA["_account_id"],
        gerrit=mock_gerrit,
    )
    return account


@pytest.fixture
def mock_project(mock_gerrit):
    """Return a pre-initialised GerritProject backed by mock_gerrit."""
    from gerrit.projects.project import GerritProject

    mock_gerrit.get.return_value = PROJECT_DATA
    project = GerritProject(
        project_id=PROJECT_DATA["id"],
        gerrit=mock_gerrit,
    )
    return project


@pytest.fixture
def mock_group(mock_gerrit):
    """Return a pre-initialised GerritGroup backed by mock_gerrit."""
    from gerrit.groups.group import GerritGroup

    mock_gerrit.get.return_value = GROUP_DATA
    group = GerritGroup(
        group_id=GROUP_DATA["id"],
        gerrit=mock_gerrit,
    )
    return group
