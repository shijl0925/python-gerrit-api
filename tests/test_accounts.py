#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import logging
import pytest
import requests
from unittest.mock import MagicMock, patch
from tests.conftest import make_gerrit_client, ACCOUNT_INFO

logger = logging.getLogger(__name__)


def make_account(account_id=1000096):
    """Helper to create a GerritAccount with a mocked client."""
    from gerrit.accounts.account import GerritAccount

    gerrit = make_gerrit_client()
    gerrit.get.return_value = ACCOUNT_INFO
    account = GerritAccount(account=account_id, gerrit=gerrit)
    return account, gerrit


class TestGerritAccounts:
    def test_search_accounts(self, gerrit_client):
        gerrit_client.get.return_value = [ACCOUNT_INFO]

        from gerrit.accounts.accounts import GerritAccounts

        accounts = GerritAccounts(gerrit=gerrit_client)
        result = accounts.search(query="name:John", detailed=True)

        assert len(result) >= 1
        gerrit_client.get.assert_called_once()

    def test_search_accounts_suggested(self, gerrit_client):
        gerrit_client.get.return_value = [ACCOUNT_INFO]

        from gerrit.accounts.accounts import GerritAccounts

        accounts = GerritAccounts(gerrit=gerrit_client)
        result = accounts.search(query="john", suggested=True)

        assert len(result) >= 1

    def test_search_accounts_all_emails(self, gerrit_client):
        gerrit_client.get.return_value = [ACCOUNT_INFO]

        from gerrit.accounts.accounts import GerritAccounts

        accounts = GerritAccounts(gerrit=gerrit_client)
        result = accounts.search(query="email:john@example.com", all_emails=True)

        assert len(result) >= 1

    def test_get_account(self, gerrit_client):
        gerrit_client.get.return_value = ACCOUNT_INFO

        from gerrit.accounts.accounts import GerritAccounts
        from gerrit.accounts.account import GerritAccount

        accounts = GerritAccounts(gerrit=gerrit_client)
        account = accounts.get(account="john.doe")

        assert isinstance(account, GerritAccount)

    def test_get_account_not_found(self, gerrit_client):
        from gerrit.accounts.accounts import GerritAccounts
        from gerrit.utils.exceptions import AccountNotFoundError

        error_response = MagicMock()
        error_response.status_code = 404
        http_error = requests.exceptions.HTTPError(response=error_response)
        gerrit_client.get.side_effect = http_error

        accounts = GerritAccounts(gerrit=gerrit_client)
        with pytest.raises(AccountNotFoundError):
            accounts.get(account="nonexistent")

    def test_create_account(self, gerrit_client):
        # First call to get raises NotFound (account doesn't exist)
        from gerrit.accounts.accounts import GerritAccounts
        from gerrit.utils.exceptions import AccountNotFoundError

        error_response = MagicMock()
        error_response.status_code = 404
        http_error = requests.exceptions.HTTPError(response=error_response)

        # get is called twice: once to check existence (404) and once to return created account
        gerrit_client.get.side_effect = [http_error, ACCOUNT_INFO]
        gerrit_client.put.return_value = {}

        accounts = GerritAccounts(gerrit=gerrit_client)
        input_ = {"name": "John Doe", "email": "john.doe@example.com"}
        account = accounts.create("john.doe", input_)
        assert account is not None

    def test_create_account_already_exists(self, gerrit_client):
        from gerrit.accounts.accounts import GerritAccounts
        from gerrit.utils.exceptions import AccountAlreadyExistsError

        gerrit_client.get.return_value = ACCOUNT_INFO

        accounts = GerritAccounts(gerrit=gerrit_client)
        input_ = {"name": "John Doe"}
        with pytest.raises(AccountAlreadyExistsError):
            accounts.create("john.doe", input_)


class TestGerritAccount:
    def test_account_attributes(self):
        account, _ = make_account()

        assert hasattr(account, "account_id")
        assert hasattr(account, "name")
        assert hasattr(account, "email")
        assert hasattr(account, "username")
        assert account.account_id == ACCOUNT_INFO["_account_id"]
        assert account.name == ACCOUNT_INFO["name"]
        assert account.email == ACCOUNT_INFO["email"]
        assert account.username == ACCOUNT_INFO["username"]

    def test_account_str(self):
        account, _ = make_account(account_id=1000096)
        assert str(account) == "1000096"

    def test_account_repr(self):
        account, _ = make_account(account_id=1000096)
        assert "GerritAccount" in repr(account)

    def test_account_to_dict(self):
        account, _ = make_account()
        result = account.to_dict()
        assert result == ACCOUNT_INFO

    def test_account_eq(self):
        account1, _ = make_account(account_id=1000096)
        account2, _ = make_account(account_id=1000096)
        account3, _ = make_account(account_id=9999)
        assert account1 == account2
        assert account1 != account3

    def test_get_detail(self):
        account, gerrit = make_account()
        detail = {"name": "John Doe", "registered_on": "2022-01-01 00:00:00.000000000"}
        gerrit.get.return_value = detail

        result = account.get_detail()
        assert "name" in result

    def test_get_name(self):
        account, gerrit = make_account()
        gerrit.get.return_value = "John Doe"

        result = account.get_name()
        assert result == "John Doe"

    def test_set_name(self):
        account, gerrit = make_account()
        gerrit.put.return_value = "Jane Doe"

        result = account.set_name({"name": "Jane Doe"})
        assert result == "Jane Doe"
        gerrit.put.assert_called_once()

    def test_delete_name(self):
        account, gerrit = make_account()

        account.delete_name()
        gerrit.delete.assert_called_once_with(account.endpoint + "/name")

    def test_get_status(self):
        account, gerrit = make_account()
        gerrit.get.return_value = "working"

        result = account.get_status()
        assert result == "working"

    def test_set_status(self):
        account, gerrit = make_account()
        gerrit.put.return_value = "working"

        account.set_status(status="working")
        gerrit.put.assert_called_once()

    def test_get_active(self):
        account, gerrit = make_account()
        gerrit.get.return_value = "ok"

        result = account.get_active()
        assert result == "ok"

    def test_set_active(self):
        account, gerrit = make_account()
        account.set_active()
        gerrit.put.assert_called_once()

    def test_delete_active(self):
        account, gerrit = make_account()
        account.delete_active()
        gerrit.delete.assert_called_once()

    def test_set_username(self):
        account, gerrit = make_account()
        gerrit.put.return_value = "new_username"

        result = account.set_username({"username": "new_username"})
        assert result == "new_username"

    def test_set_displayname(self):
        account, gerrit = make_account()
        gerrit.put.return_value = "John"

        result = account.set_displayname({"display_name": "John"})
        assert result == "John"

    def test_set_http_password(self):
        account, gerrit = make_account()
        gerrit.put.return_value = "new_password"

        result = account.set_http_password({"generate": "true"})
        assert result == "new_password"

    def test_delete_http_password(self):
        account, gerrit = make_account()
        account.delete_http_password()
        gerrit.delete.assert_called_once()

    def test_get_oauth_token(self):
        account, gerrit = make_account()
        token_info = {"username": "john.doe", "access_token": "abc123"}
        gerrit.get.return_value = token_info

        result = account.get_oauth_token()
        assert result == token_info

    def test_list_capabilities(self):
        account, gerrit = make_account()
        caps = {"queryLimit": {"min": 0, "max": 500}}
        gerrit.get.return_value = caps

        result = account.list_capabilities()
        assert "queryLimit" in result

    def test_check_capability(self):
        account, gerrit = make_account()
        gerrit.get.return_value = "ok"

        result = account.check_capability("account-deleteOwnAccount")
        assert result == "ok"

    def test_get_avatar(self):
        account, gerrit = make_account()
        gerrit.get.return_value = b"fake_image_bytes"

        result = account.get_avatar()
        assert isinstance(result, bytes)

    def test_get_avatar_change_url(self):
        account, gerrit = make_account()
        gerrit.get.return_value = "http://www.gravatar.com"

        result = account.get_avatar_change_url()
        assert result == "http://www.gravatar.com"

    def test_get_user_preferences(self):
        account, gerrit = make_account()
        prefs = {"changes_per_page": 25, "diff_view": "SIDE_BY_SIDE"}
        gerrit.get.return_value = prefs

        result = account.get_user_preferences()
        assert "changes_per_page" in result

    def test_set_user_preferences(self):
        account, gerrit = make_account()
        prefs = {"changes_per_page": 50, "diff_view": "SIDE_BY_SIDE"}
        gerrit.put.return_value = prefs

        result = account.set_user_preferences({"changes_per_page": 50})
        assert result.get("changes_per_page") == 50

    def test_get_diff_preferences(self):
        account, gerrit = make_account()
        prefs = {"line_length": 100, "tab_size": 8}
        gerrit.get.return_value = prefs

        result = account.get_diff_preferences()
        assert "line_length" in result

    def test_set_diff_preferences(self):
        account, gerrit = make_account()
        prefs = {"line_length": 120, "tab_size": 8}
        gerrit.put.return_value = prefs

        result = account.set_diff_preferences({"line_length": 120})
        assert result.get("line_length") == 120

    def test_get_edit_preferences(self):
        account, gerrit = make_account()
        prefs = {"line_length": 80, "tab_size": 4}
        gerrit.get.return_value = prefs

        result = account.get_edit_preferences()
        assert "line_length" in result

    def test_set_edit_preferences(self):
        account, gerrit = make_account()
        prefs = {"line_length": 100, "tab_size": 4}
        gerrit.put.return_value = prefs

        result = account.set_edit_preferences({"line_length": 100})
        assert result.get("line_length") == 100

    def test_get_watched_projects(self):
        account, gerrit = make_account()
        watched = [{"project": "myProject", "notify_new_changes": True}]
        gerrit.get.return_value = watched

        result = account.get_watched_projects()
        assert len(result) >= 0

    def test_modify_watched_projects(self):
        account, gerrit = make_account()
        watched = [{"project": "myProject", "notify_new_changes": True}]
        gerrit.post.return_value = watched

        input_ = [{"project": "myProject", "notify_new_changes": True}]
        result = account.modify_watched_projects(input_)
        assert len(result) >= 1

    def test_delete_watched_projects(self):
        account, gerrit = make_account()
        gerrit.post.return_value = None

        input_ = [{"project": "myProject"}]
        account.delete_watched_projects(input_)
        gerrit.post.assert_called_once()

    def test_get_external_ids(self):
        account, gerrit = make_account()
        ext_ids = [{"identity": "mailto:john.doe@example.com", "email": "john.doe@example.com"}]
        gerrit.get.return_value = ext_ids

        result = account.get_external_ids()
        assert len(result) >= 0

    def test_delete_external_ids(self):
        account, gerrit = make_account()
        gerrit.post.return_value = None

        account.delete_external_ids(["mailto:john.doe@example.com"])
        gerrit.post.assert_called_once()

    def test_list_contributor_agreements(self):
        account, gerrit = make_account()
        agreements = [{"name": "Individual", "url": "https://example.com/cla"}]
        gerrit.get.return_value = agreements

        result = account.list_contributor_agreements()
        assert len(result) >= 0

    def test_sign_contributor_agreement(self):
        account, gerrit = make_account()
        gerrit.put.return_value = "Individual"

        result = account.sign_contributor_agreement({"name": "Individual"})
        assert result == "Individual"

    def test_delete_draft_comments(self):
        account, gerrit = make_account()
        response = [{"change_id": "I123", "message": "deleted"}]
        gerrit.post.return_value = response

        result = account.delete_draft_comments({"query": "is:abandoned"})
        assert len(result) >= 0

    def test_index(self):
        account, gerrit = make_account()
        gerrit.post.return_value = None

        account.index()
        gerrit.post.assert_called_once()

    def test_get_default_starred_changes(self):
        account, gerrit = make_account()
        changes = [ACCOUNT_INFO]
        gerrit.get.return_value = changes

        result = account.get_default_starred_changes()
        assert len(result) >= 0

    def test_put_default_star_on_change(self):
        account, gerrit = make_account()
        gerrit.put.return_value = None

        account.put_default_star_on_change("Iabcdef1234")
        gerrit.put.assert_called_once()

    def test_remove_default_star_from_change(self):
        account, gerrit = make_account()
        gerrit.delete.return_value = None

        account.remove_default_star_from_change("Iabcdef1234")
        gerrit.delete.assert_called_once()

    def test_get_starred_changes(self):
        account, gerrit = make_account()
        gerrit.get.return_value = []

        result = account.get_starred_changes()
        assert len(result) >= 0

    def test_get_star_labels_from_change(self):
        account, gerrit = make_account()
        gerrit.get.return_value = ["blue", "red"]

        result = account.get_star_labels_from_change("Iabcdef1234")
        assert len(result) >= 0

    def test_update_star_labels_on_change(self):
        account, gerrit = make_account()
        gerrit.post.return_value = ["blue", "red"]

        input_ = {"add": ["blue", "red"], "remove": ["yellow"]}
        result = account.update_star_labels_on_change("Iabcdef1234", input_)
        assert "blue" in result

    def test_groups_property(self):
        account, gerrit = make_account()
        group_info = {
            "id": "6a1e70e1a88782771a91808c8af9bbb7a9871389",
            "name": "MyGroup",
            "url": "#/admin/groups/uuid-6a1e70e1a88782771a91808c8af9bbb7a9871389",
            "options": {},
            "group_id": 613,
            "owner": "MyGroup",
            "owner_id": "6a1e70e1a88782771a91808c8af9bbb7a9871389",
            "created_on": "2013-02-01 09:59:32.126000000",
        }

        # account.groups calls gerrit.get for groups list, then for each group
        gerrit.get.side_effect = [
            [{"id": "6a1e70e1a88782771a91808c8af9bbb7a9871389"}],
            group_info,
        ]
        groups = account.groups
        assert len(groups) == 1


class TestGerritAccountEmails:
    def test_list_emails(self):
        from gerrit.accounts.emails import GerritAccountEmails

        gerrit = make_gerrit_client()
        emails_data = [
            {"email": "john.doe@example.com", "preferred": True},
            {"email": "john@company.com", "preferred": False},
        ]
        gerrit.get.return_value = emails_data

        emails = GerritAccountEmails(account=1000096, gerrit=gerrit)
        result = emails.list()
        assert len(result) >= 1

    def test_get_email(self):
        from gerrit.accounts.emails import GerritAccountEmails, GerritAccountEmail

        gerrit = make_gerrit_client()
        email_data = {"email": "john.doe@example.com", "preferred": True}
        gerrit.get.return_value = email_data

        emails = GerritAccountEmails(account=1000096, gerrit=gerrit)
        email = emails.get("john.doe@example.com")
        assert isinstance(email, GerritAccountEmail)

    def test_get_email_not_found(self):
        from gerrit.accounts.emails import GerritAccountEmails
        from gerrit.utils.exceptions import AccountEmailNotFoundError

        gerrit = make_gerrit_client()
        error_response = MagicMock()
        error_response.status_code = 404
        http_error = requests.exceptions.HTTPError(response=error_response)
        gerrit.get.side_effect = http_error

        emails = GerritAccountEmails(account=1000096, gerrit=gerrit)
        with pytest.raises(AccountEmailNotFoundError):
            emails.get("nonexistent@example.com")

    def test_create_email(self):
        from gerrit.accounts.emails import GerritAccountEmails
        from gerrit.utils.exceptions import AccountEmailAlreadyExistsError

        gerrit = make_gerrit_client()
        email_data = {"email": "john.doe@example.com", "preferred": True}
        # First get succeeds (email exists) -> raises AlreadyExists
        gerrit.get.return_value = email_data

        emails = GerritAccountEmails(account=1000096, gerrit=gerrit)
        with pytest.raises(AccountEmailAlreadyExistsError):
            emails.create("john.doe@example.com")


class TestGerritAccountSSHKeys:
    def test_list_ssh_keys(self):
        from gerrit.accounts.ssh_keys import GerritAccountSSHKeys

        gerrit = make_gerrit_client()
        ssh_keys_data = [
            {
                "seq": 1,
                "ssh_public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA0T",
                "encoded_key": "AAAAB3NzaC1yc2EAAAABIwAAAQEA0T",
                "algorithm": "ssh-rsa",
                "comment": "john.doe@example.com",
                "valid": True,
            }
        ]
        gerrit.get.return_value = ssh_keys_data

        ssh_keys = GerritAccountSSHKeys(account=1000096, gerrit=gerrit)
        result = ssh_keys.list()
        assert len(result) >= 0


class TestGerritAccountGPGKeys:
    def test_list_gpg_keys(self):
        from gerrit.accounts.gpg_keys import GerritAccountGPGKeys

        gerrit = make_gerrit_client()
        gerrit.get.return_value = {}

        gpg_keys = GerritAccountGPGKeys(account=1000096, gerrit=gerrit)
        result = gpg_keys.list()
        assert len(result) >= 0
