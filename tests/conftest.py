#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import pytest
from unittest.mock import MagicMock, patch


ACCOUNT_INFO = {
    "_account_id": 1000096,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "username": "john.doe",
    "avatars": [{"url": "https://example.com/avatar.jpg", "height": 26}],
    "registered_on": "2022-01-01 00:00:00.000000000",
}

CHANGE_INFO = {
    "id": "myProject~master~I8473b95934b5732ac55d26311a706c9c2bde9940",
    "project": "myProject",
    "branch": "master",
    "hashtags": [],
    "change_id": "I8473b95934b5732ac55d26311a706c9c2bde9940",
    "subject": "Implementing Feature X",
    "status": "NEW",
    "created": "2023-01-01 00:00:00.000000000",
    "updated": "2023-01-02 00:00:00.000000000",
    "_number": 3965,
    "owner": {"_account_id": 1000096},
    "insertions": 10,
    "deletions": 2,
}

PROJECT_INFO = {
    "id": "myProject",
    "name": "myProject",
    "parent": "All-Projects",
    "state": "ACTIVE",
    "labels": {"Code-Review": {}},
    "web_links": [{"name": "browse", "url": "https://example.com/myProject"}],
    "description": "My demo project",
}

GROUP_INFO = {
    "id": "6a1e70e1a88782771a91808c8af9bbb7a9871389",
    "name": "MyGroup",
    "url": "#/admin/groups/uuid-6a1e70e1a88782771a91808c8af9bbb7a9871389",
    "options": {},
    "description": "contains all committers",
    "group_id": 613,
    "owner": "MyGroup",
    "owner_id": "6a1e70e1a88782771a91808c8af9bbb7a9871389",
    "created_on": "2013-02-01 09:59:32.126000000",
    "members": [],
    "includes": [],
}


def make_gerrit_client():
    """Create a GerritClient with mocked HTTP methods."""
    from gerrit import GerritClient

    client = GerritClient.__new__(GerritClient)
    client._base_url = "http://localhost:8080"
    client.auth_suffix = "/a"
    client.default_headers = {"Content-Type": "application/json; charset=UTF-8"}
    client.get = MagicMock(return_value={})
    client.post = MagicMock(return_value={})
    client.put = MagicMock(return_value={})
    client.delete = MagicMock(return_value=None)
    client.session = MagicMock()
    client.requester = MagicMock()
    return client


@pytest.fixture(scope="function")
def gerrit_client():
    return make_gerrit_client()


@pytest.fixture(scope="function")
def gitiles_client():
    from gitiles import GitilesClient

    client = GitilesClient.__new__(GitilesClient)
    client._base_url = "https://gerrit.googlesource.com"
    client.session = MagicMock()
    client.requester = MagicMock()
    return client


CHANGE_ID = "myProject~master~I8473b95934b5732ac55d26311a706c9c2bde9940"

status = ("open", "merged", "abandoned")


@pytest.fixture(params=status)
def change_status(request):
    return request.param


@pytest.fixture(scope="function")
def latest_change_id():
    return CHANGE_ID
