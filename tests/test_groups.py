#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import logging
import pytest
from gerrit.groups.group import GerritGroup

logger = logging.getLogger(__name__)


def test_list_groups(gerrit_client):
    resp = gerrit_client.groups.list(limit=25, skip=0)

    assert len(resp) > 0


def test_search_groups(gerrit_client):
    group_name = "Reviewers"
    query = f"name:{group_name}"
    resp = gerrit_client.groups.search(query=query)

    assert len(resp) == 1


def test_get_group(gerrit_client):
    from gerrit.utils.exceptions import GroupNotFoundError
    with pytest.raises(GroupNotFoundError):
        gerrit_client.groups.get(id_=1000000000)

    group_id = 613
    group = gerrit_client.groups.get(group_id)

    assert isinstance(group, GerritGroup)

    assert str(group) == str(group.id)

    group_name = group.get_name()
    assert group_name == "Reviewers"

    group_info = group.to_dict()
    assert group_info.get("name") == "Reviewers"

    group_detail = group.get_detail()
    assert "members" in group_detail

    group_options = group.get_options()
    assert "visible_to_all" in group_options

    group_owner = group.get_owner()
    assert "name" in group_owner


@pytest.mark.xfail(reason="Request is not authorized")
def test_create_group(gerrit_client):
    from gerrit.utils.exceptions import GroupAlreadyExistsError
    input_ = {
        "description": "contains all committers for MyProject2",
        "visible_to_all": 'true',
        "owner": "Administrators",
        "owner_id": "af01a8cb8cbd8ee7be072b98b1ee882867c0cf06"
    }
    group_name = "Reviewers"
    with pytest.raises(GroupAlreadyExistsError):
        gerrit_client.groups.create(group_name, input_)

    group = gerrit_client.groups.create('My-Project2-Committers', input_)
    assert group.name == "My-Project2-Committers"


def test_group_members(gerrit_client):
    group_id = 613
    group = gerrit_client.groups.get(group_id)
    members = group.members.list()
    assert len(members) > 0


@pytest.mark.xfail(reason="Request is not authorized")
def test_add_group_member(gerrit_client):
    group_id = 613
    group = gerrit_client.groups.get(group_id)

    account_id = 16
    from gerrit.utils.exceptions import GroupMemberAlreadyExistsError
    with pytest.raises(GroupMemberAlreadyExistsError):
        group.members.add(account_id)

    user = gerrit_client.accounts.get(account="jialiang.shi")
    account_id = user.account_id
    logger.debug(f"account id: {account_id}")
    group.members.add(account_id)


def test_group_member(gerrit_client):
    group_id = 613
    group = gerrit_client.groups.get(group_id)

    account_id = 16
    member = group.members.get(account_id)
    assert str(member) == str(account_id)

    result = member.to_dict()
    assert "_account_id" in result

    from gerrit.utils.exceptions import GroupMemberNotFoundError
    with pytest.raises(GroupMemberNotFoundError):
        group.members.get(account=0)


@pytest.mark.xfail(reason="Request is not authorized")
def test_remove_group_member(gerrit_client):
    group_id = 613
    group = gerrit_client.groups.get(group_id)

    account_id = 16
    group.members.remove(account_id)


def test_group_subgroups(gerrit_client):
    group_id = 613
    group = gerrit_client.groups.get(group_id)
    subgroups = group.subgroup.list()
    assert len(subgroups) > 0

    subgroup_id = "3bff52be902fb279c5e495462a68b701e9bd5889"
    subgroup = group.subgroup.get(subgroup_id)
    assert str(subgroup) == subgroup_id
