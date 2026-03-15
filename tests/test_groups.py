#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
"""
Unit tests for gerrit.groups — all HTTP calls are mocked.
"""
import logging
import pytest
import requests
from unittest.mock import MagicMock

from tests.conftest import GROUP_DATA, ACCOUNT_DATA

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# GerritGroups (manager)
# ---------------------------------------------------------------------------

class TestGerritGroups:

    def test_list_groups(self, mock_gerrit):
        mock_gerrit.get.return_value = [GROUP_DATA]

        from gerrit.groups.groups import GerritGroups
        groups = GerritGroups(gerrit=mock_gerrit)
        result = groups.list(limit=25, skip=0)
        assert len(result) >= 1

    def test_list_groups_with_options(self, mock_gerrit):
        mock_gerrit.get.return_value = [GROUP_DATA]

        from gerrit.groups.groups import GerritGroups
        groups = GerritGroups(gerrit=mock_gerrit)
        result = groups.list(options=["MEMBERS"], limit=10)
        assert isinstance(result, list)

    def test_list_groups_with_pattern(self, mock_gerrit):
        mock_gerrit.get.return_value = [GROUP_DATA]

        from gerrit.groups.groups import GerritGroups
        groups = GerritGroups(gerrit=mock_gerrit)
        result = groups.list(pattern_dispatcher={"match": "My"})
        assert isinstance(result, list)

    def test_search_groups(self, mock_gerrit):
        mock_gerrit.get.return_value = [GROUP_DATA]

        from gerrit.groups.groups import GerritGroups
        groups = GerritGroups(gerrit=mock_gerrit)
        result = groups.search(query="name:MyGroup")
        assert len(result) >= 1

    def test_get_group(self, mock_gerrit):
        mock_gerrit.get.return_value = GROUP_DATA

        from gerrit.groups.groups import GerritGroups
        from gerrit.groups.group import GerritGroup
        groups = GerritGroups(gerrit=mock_gerrit)
        group = groups.get("6a1e70e1a88782771a91808c8af9bbb7a9871389")
        assert isinstance(group, GerritGroup)

    def test_get_group_not_found(self, mock_gerrit):
        response_mock = MagicMock()
        response_mock.status_code = 404
        http_error = requests.exceptions.HTTPError(response=response_mock)
        mock_gerrit.get.side_effect = http_error

        from gerrit.groups.groups import GerritGroups
        from gerrit.utils.exceptions import GroupNotFoundError
        groups = GerritGroups(gerrit=mock_gerrit)
        with pytest.raises(GroupNotFoundError):
            groups.get(1000000000)

    def test_create_group(self, mock_gerrit):
        response_mock = MagicMock()
        response_mock.status_code = 404
        http_error = requests.exceptions.HTTPError(response=response_mock)
        mock_gerrit.get.side_effect = [http_error, GROUP_DATA, GROUP_DATA]

        from gerrit.groups.groups import GerritGroups
        groups = GerritGroups(gerrit=mock_gerrit)
        result = groups.create("NewGroup", {"description": "A new group"})
        assert result is not None
        mock_gerrit.put.assert_called_once()

    def test_create_group_already_exists(self, mock_gerrit):
        mock_gerrit.get.return_value = GROUP_DATA

        from gerrit.groups.groups import GerritGroups
        from gerrit.utils.exceptions import GroupAlreadyExistsError
        groups = GerritGroups(gerrit=mock_gerrit)
        with pytest.raises(GroupAlreadyExistsError):
            groups.create("MyGroup", {})


# ---------------------------------------------------------------------------
# GerritGroup (single group)
# ---------------------------------------------------------------------------

class TestGerritGroup:

    def test_group_str(self, mock_group):
        assert str(mock_group) == GROUP_DATA["id"]

    def test_group_repr(self, mock_group):
        assert "GerritGroup" in repr(mock_group)

    def test_group_to_dict(self, mock_group):
        info = mock_group.to_dict()
        assert info.get("name") == GROUP_DATA["name"]

    def test_get_name(self, mock_group):
        mock_group.gerrit.get.return_value = "MyGroup"
        result = mock_group.get_name()
        assert result == "MyGroup"

    def test_get_detail(self, mock_group):
        detail = {"members": [ACCOUNT_DATA], "includes": []}
        mock_group.gerrit.get.return_value = detail
        result = mock_group.get_detail()
        assert "members" in result

    def test_set_name(self, mock_group):
        mock_group.gerrit.put.return_value = "NewName"
        mock_group.set_name({"name": "NewName"})
        mock_group.gerrit.put.assert_called()

    def test_get_description(self, mock_group):
        mock_group.gerrit.get.return_value = "A test group"
        result = mock_group.get_description()
        assert result == "A test group"

    def test_set_description(self, mock_group):
        mock_group.gerrit.put.return_value = "Updated description"
        mock_group.set_description({"description": "Updated"})
        mock_group.gerrit.put.assert_called()

    def test_get_options(self, mock_group):
        options = {"visible_to_all": True}
        mock_group.gerrit.get.return_value = options
        result = mock_group.get_options()
        assert "visible_to_all" in result

    def test_set_options(self, mock_group):
        mock_group.gerrit.put.return_value = {"visible_to_all": False}
        mock_group.set_options({"visible_to_all": False})
        mock_group.gerrit.put.assert_called()

    def test_get_owner(self, mock_group):
        owner = {"name": "Administrators"}
        mock_group.gerrit.get.return_value = owner
        result = mock_group.get_owner()
        assert "name" in result

    def test_set_owner(self, mock_group):
        mock_group.gerrit.put.return_value = {"name": "NewOwner"}
        mock_group.set_owner({"owner": "NewOwner"})
        mock_group.gerrit.put.assert_called()

    def test_group_equality(self, mock_group, mock_gerrit):
        mock_gerrit.get.return_value = GROUP_DATA
        from gerrit.groups.group import GerritGroup
        other = GerritGroup(group_id=GROUP_DATA["id"], gerrit=mock_gerrit)
        assert mock_group == other

    def test_group_inequality(self, mock_group, mock_gerrit):
        other_data = {**GROUP_DATA, "id": "different_id"}
        mock_gerrit.get.return_value = other_data
        from gerrit.groups.group import GerritGroup
        other = GerritGroup(group_id="different_id", gerrit=mock_gerrit)
        assert mock_group != other


# ---------------------------------------------------------------------------
# GerritGroupMembers
# ---------------------------------------------------------------------------

class TestGerritGroupMembers:

    def test_list_members(self, mock_group):
        mock_group.gerrit.get.return_value = [{"_account_id": 1000096}]
        mock_group.gerrit.accounts.get.return_value = MagicMock()
        members = mock_group.members.list()
        assert len(members) >= 1

    def test_get_member(self, mock_group):
        mock_group.gerrit.get.return_value = {"_account_id": 1000096, "name": "Test User"}
        mock_group.gerrit.accounts.get.return_value = MagicMock(account_id=1000096)
        member = mock_group.members.get(1000096)
        assert member is not None

    def test_get_member_not_found(self, mock_group):
        response_mock = MagicMock()
        response_mock.status_code = 404
        http_error = requests.exceptions.HTTPError(response=response_mock)
        mock_group.gerrit.get.side_effect = http_error

        from gerrit.utils.exceptions import GroupMemberNotFoundError
        with pytest.raises(GroupMemberNotFoundError):
            mock_group.members.get(account=0)

    def test_add_member_already_exists(self, mock_group):
        mock_group.gerrit.get.return_value = {"_account_id": 1000096}
        mock_group.gerrit.accounts.get.return_value = MagicMock()

        from gerrit.utils.exceptions import GroupMemberAlreadyExistsError
        with pytest.raises(GroupMemberAlreadyExistsError):
            mock_group.members.add(1000096)

    def test_add_member_new(self, mock_group):
        response_mock = MagicMock()
        response_mock.status_code = 404
        http_error = requests.exceptions.HTTPError(response=response_mock)
        member_mock = MagicMock()
        mock_group.gerrit.get.side_effect = [http_error, {"_account_id": 999}]
        mock_group.gerrit.accounts.get.return_value = member_mock

        result = mock_group.members.add(999)
        assert result is not None
        mock_group.gerrit.put.assert_called()

    def test_remove_member(self, mock_group):
        mock_group.gerrit.get.return_value = {"_account_id": 1000096}
        mock_group.gerrit.accounts.get.return_value = MagicMock()
        mock_group.members.remove(1000096)
        mock_group.gerrit.delete.assert_called()

    def test_add_members_batch(self, mock_group):
        members_info = [{"_account_id": 1000096}, {"_account_id": 1000097}]
        mock_group.gerrit.post.return_value = members_info
        result = mock_group.members.add_members({"members": ["jane.roe", "john.doe"]})
        mock_group.gerrit.post.assert_called()
        call_args = mock_group.gerrit.post.call_args
        assert call_args[0][0].endswith("/members")

    def test_remove_members_batch(self, mock_group):
        mock_group.members.remove_members({"members": ["jane.roe", "john.doe"]})
        mock_group.gerrit.post.assert_called()
        call_args = mock_group.gerrit.post.call_args
        assert call_args[0][0].endswith("/members.delete")


# ---------------------------------------------------------------------------
# GerritGroupSubGroups
# ---------------------------------------------------------------------------

class TestGerritGroupSubGroups:

    def test_list_subgroups(self, mock_group):
        subgroup_data = {**GROUP_DATA, "id": "sub_group_id"}
        mock_group.gerrit.get.return_value = [{"id": "sub_group_id"}]
        mock_group.gerrit.groups.get.return_value = MagicMock()
        subgroups = mock_group.subgroup.list()
        assert len(subgroups) >= 1

    def test_get_subgroup(self, mock_group):
        subgroup_data = {**GROUP_DATA, "id": "sub_group_id"}
        mock_group.gerrit.get.return_value = subgroup_data
        mock_group.gerrit.groups.get.return_value = MagicMock(id="sub_group_id")
        subgroup = mock_group.subgroup.get("sub_group_id")
        assert subgroup is not None

    def test_add_subgroup(self, mock_group):
        subgroup_data = {**GROUP_DATA, "id": "sub_group_id"}
        mock_group.gerrit.put.return_value = subgroup_data
        mock_group.gerrit.groups.get.return_value = MagicMock(id="sub_group_id")
        mock_group.subgroup.add("sub_group_id")
        mock_group.gerrit.put.assert_called()

    def test_remove_subgroup(self, mock_group):
        mock_group.subgroup.remove("sub_group_id")
        mock_group.gerrit.delete.assert_called()

    def test_add_subgroups_batch(self, mock_group):
        subgroups_info = [{"id": "sub_group_id"}]
        mock_group.gerrit.post.return_value = subgroups_info
        result = mock_group.subgroup.add_subgroups({"groups": ["MyGroup", "MyOtherGroup"]})
        mock_group.gerrit.post.assert_called()
        call_args = mock_group.gerrit.post.call_args
        assert call_args[0][0].endswith("/groups")

    def test_remove_subgroups_batch(self, mock_group):
        mock_group.subgroup.remove_subgroups({"groups": ["MyGroup", "MyOtherGroup"]})
        mock_group.gerrit.post.assert_called()
        call_args = mock_group.gerrit.post.call_args
        assert call_args[0][0].endswith("/groups.delete")

