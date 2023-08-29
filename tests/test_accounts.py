#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import logging
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.parametrize('query', ["name:Alex", "is:active", "username:abeid68", "email:abeid2168@gmail.com"])
def test_search_accounts(gerrit_client, query):
    resp = gerrit_client.accounts.search(query=query, detailed=True)

    assert len(resp) >= 1


def test_get_account(gerrit_client):
    from gerrit.utils.exceptions import AccountNotFoundError
    with pytest.raises(AccountNotFoundError):
        gerrit_client.accounts.get(account="keven.shi")

    username = "alek1231234"
    account = gerrit_client.accounts.get(account=username)

    logger.debug(account.to_dict())

    attrs = ["account_id", "name", "email", "username", "avatars"]
    for attr in attrs:
        logger.debug(f"{attr}, {hasattr(account, attr)}, {getattr(account, attr)}")

    assert all([hasattr(account, attr) for attr in attrs])

    assert "username" in account.to_dict()
    assert "email" in account.to_dict()


def test_get_account_detail(gerrit_client):
    username = "alek1231234"
    account = gerrit_client.accounts.get(account=username)

    result = account.get_detail()
    assert "name" in result


def test_get_account_name(gerrit_client):
    username = "alek1231234"
    account = gerrit_client.accounts.get(account=username)

    result = account.get_name()

    assert len(result) > 0


def test_get_account_active(gerrit_client):
    username = "alek1231234"
    account = gerrit_client.accounts.get(account=username)

    result = account.get_active()

    assert result == "ok"


def test_get_account_emails(gerrit_client):
    account = gerrit_client.accounts.get(account="self")
    emails = account.emails.list()
    assert len(emails) > 0


def test_get_account_email(gerrit_client):
    from gerrit.utils.exceptions import AccountEmailNotFoundError
    account = gerrit_client.accounts.get(account="self")

    with pytest.raises(AccountEmailNotFoundError):
        account.emails.get(email="111111111@qq.com")

    email_address = 'kevin09254930sjl@gmail.com'
    email = account.emails.get(email_address)

    result = email.to_dict()
    assert result.get("email") == email_address
    assert result.get("preferred")


def test_register_account_email(gerrit_client):
    from gerrit.utils.exceptions import AccountEmailAlreadyExistsError
    account = gerrit_client.accounts.get(account="self")

    with pytest.raises(AccountEmailAlreadyExistsError):
        account.emails.create(email='kevin09254930sjl@gmail.com')


def test_delete_account_name(gerrit_client):
    account = gerrit_client.accounts.get(account="self")
    account.delete_name()


def test_set_account_name(gerrit_client):
    account = gerrit_client.accounts.get(account="self")
    input_ = {
        "name": "Keven Shi"
    }
    account.set_name(input_)


def test_set_account_status(gerrit_client):
    account = gerrit_client.accounts.get(account="self")
    account.set_status(status="working")


def test_get_account_status(gerrit_client):
    account = gerrit_client.accounts.get(account="self")
    result = account.get_status()

    assert "working" == result


def test_set_account__display_name(gerrit_client):
    account = gerrit_client.accounts.get(account="self")
    input_ = {
        "display_name": "Kevin"
    }
    account.set_displayname(input_)


@pytest.mark.xfail(reason="Request is not authorized")
def test_set_account_active(gerrit_client):
    account = gerrit_client.accounts.get(account="self")

    account.set_active()


@pytest.mark.xfail(reason="Request is not authorized")
def test_delete_account_active(gerrit_client):
    account = gerrit_client.accounts.get(account="self")

    account.delete_active()


def test_list_account_ssh_keys(gerrit_client):
    account = gerrit_client.accounts.get(account="self")
    ssh_keys = account.ssh_keys.list()
    logger.debug(f"the number of account ssh keys: {len(ssh_keys)}")

    assert len(ssh_keys) >= 0


def test_list_account_gpg_keys(gerrit_client):
    account = gerrit_client.accounts.get(account="self")
    gpg_keys = account.gpg_keys.list()
    logger.debug(f"the number of account gpg keys: {len(gpg_keys)}")

    assert len(gpg_keys) >= 0


def test_list_account_capabilities(gerrit_client):
    account = gerrit_client.accounts.get(account="self")

    result = account.list_capabilities()

    assert "queryLimit" in result


def test_check_account_capability(gerrit_client):
    account = gerrit_client.accounts.get(account="self")

    capability = "account-deleteOwnAccount"
    result = account.check_capability(capability)
    assert result == "ok"

    capability = "createGroup"
    import requests
    with pytest.raises(requests.exceptions.HTTPError):
        account.check_capability(capability)


def test_get_account_groups(gerrit_client):
    account = gerrit_client.accounts.get(account="self")

    groups = account.groups
    assert len(groups) > 0


def test_get_account_avatar(gerrit_client):
    account = gerrit_client.accounts.get(account="self")

    avatar = account.get_avatar()
    assert isinstance(avatar, bytes)


def test_get_account_avatar_change_url(gerrit_client):
    account = gerrit_client.accounts.get(account="self")

    url = account.get_avatar_change_url()
    assert url == "http://www.gravatar.com"


def test_get_account_preferences(gerrit_client):
    account = gerrit_client.accounts.get(account="self")

    res = account.get_user_preferences()

    assert "changes_per_page" in res


def test_set_account_preferences(gerrit_client):
    account = gerrit_client.accounts.get(account="self")
    input_ = {
        "changes_per_page": 50
    }
    res = account.set_user_preferences(input_)

    assert res.get("changes_per_page") == 50


def test_get_account_diff_preferences(gerrit_client):
    account = gerrit_client.accounts.get(account="self")

    res = account.get_diff_preferences()

    assert "line_length" in res


def test_set_account_diff_preferences(gerrit_client):
    account = gerrit_client.accounts.get(account="self")
    input_ = {
        "line_length": 120
    }
    res = account.set_diff_preferences(input_)

    assert res.get("line_length") == 120


def test_get_account_edit_preferences(gerrit_client):
    account = gerrit_client.accounts.get(account="self")

    res = account.get_edit_preferences()

    assert "line_length" in res


def test_set_account_edit_preferences(gerrit_client):
    account = gerrit_client.accounts.get(account="self")
    input_ = {
        "line_length": 100
    }
    res = account.set_edit_preferences(input_)

    assert res.get("line_length") == 100


def test_get_account_watched_projects(gerrit_client):
    account = gerrit_client.accounts.get(account="self")
    projects = account.get_watched_projects()

    assert len(projects) >= 0


def test_add_account_watched_projects(gerrit_client):
    account = gerrit_client.accounts.get(account="self")
    input_ = [
        {
            "project": "LineageOS/android_packages_apps_Dialer",
            "notify_new_changes": True,
            "notify_new_patch_sets": True,
            "notify_all_comments": True,
        }
    ]
    res = account.modify_watched_projects(input_)

    assert len(res) >= 1


def test_delete_account_watched_projects(gerrit_client):
    account = gerrit_client.accounts.get(account="self")
    input_ = [
        {
            "project": "LineageOS/android_packages_apps_Dialer",
            "notify_new_changes": True,
            "notify_new_patch_sets": True,
            "notify_all_comments": True,
        }
    ]
    account.delete_watched_projects(input_)
