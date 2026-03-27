#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
"""
Unit tests for gerrit.accounts — all HTTP calls are mocked so these tests
run without any real Gerrit server or credentials.
"""
import logging
import pytest
import requests
from unittest.mock import MagicMock, patch

from tests.conftest import ACCOUNT_DATA

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# GerritAccounts (manager)
# ---------------------------------------------------------------------------

class TestGerritAccounts:

    def test_search_accounts(self, mock_gerrit):
        mock_gerrit.get.return_value = [ACCOUNT_DATA]

        from gerrit.accounts.accounts import GerritAccounts
        accounts = GerritAccounts(gerrit=mock_gerrit)
        result = accounts.search(query="name:Test", detailed=True)

        assert len(result) >= 1
        mock_gerrit.get.assert_called_once()

    def test_search_accounts_with_options(self, mock_gerrit):
        mock_gerrit.get.return_value = [ACCOUNT_DATA]

        from gerrit.accounts.accounts import GerritAccounts
        accounts = GerritAccounts(gerrit=mock_gerrit)

        result = accounts.search(query="is:active", limit=10, skip=0, suggested=True)
        assert isinstance(result, list)

        result = accounts.search(query="is:active", all_emails=True)
        assert isinstance(result, list)

    def test_get_account(self, mock_gerrit):
        mock_gerrit.get.return_value = ACCOUNT_DATA

        from gerrit.accounts.accounts import GerritAccounts
        from gerrit.accounts.account import GerritAccount
        accounts = GerritAccounts(gerrit=mock_gerrit)
        account = accounts.get(account="testuser")

        assert isinstance(account, GerritAccount)
        assert account.account_id == ACCOUNT_DATA["_account_id"]

    def test_get_account_not_found(self, mock_gerrit):
        response_mock = MagicMock()
        response_mock.status_code = 404
        http_error = requests.exceptions.HTTPError(response=response_mock)
        mock_gerrit.get.side_effect = http_error

        from gerrit.accounts.accounts import GerritAccounts
        from gerrit.utils.exceptions import AccountNotFoundError
        accounts = GerritAccounts(gerrit=mock_gerrit)
        with pytest.raises(AccountNotFoundError):
            accounts.get(account="nobody")

    def test_create_account(self, mock_gerrit):
        # First call (check existence) raises 404, second call returns created account
        response_mock = MagicMock()
        response_mock.status_code = 404
        http_error = requests.exceptions.HTTPError(response=response_mock)
        mock_gerrit.get.side_effect = [http_error, ACCOUNT_DATA, ACCOUNT_DATA]

        from gerrit.accounts.accounts import GerritAccounts
        accounts = GerritAccounts(gerrit=mock_gerrit)
        result = accounts.create("newuser", {"name": "New User", "email": "new@example.com"})
        assert result is not None
        mock_gerrit.put.assert_called_once()

    def test_create_account_already_exists(self, mock_gerrit):
        mock_gerrit.get.return_value = ACCOUNT_DATA

        from gerrit.accounts.accounts import GerritAccounts
        from gerrit.utils.exceptions import AccountAlreadyExistsError
        accounts = GerritAccounts(gerrit=mock_gerrit)
        with pytest.raises(AccountAlreadyExistsError):
            accounts.create("testuser", {})


# ---------------------------------------------------------------------------
# GerritAccount (single account)
# ---------------------------------------------------------------------------

class TestGerritAccount:

    def test_account_str_and_repr(self, mock_account):
        assert str(mock_account) == str(ACCOUNT_DATA["_account_id"])
        assert "GerritAccount" in repr(mock_account)

    def test_account_attributes(self, mock_account):
        attrs = ["account_id", "name", "email", "username", "avatars"]
        for attr in attrs:
            assert hasattr(mock_account, attr), f"Missing attribute: {attr}"

    def test_account_to_dict(self, mock_account):
        info = mock_account.to_dict()
        assert info.get("_account_id") == ACCOUNT_DATA["_account_id"]
        assert info.get("username") == ACCOUNT_DATA["username"]

    def test_get_detail(self, mock_account):
        detail = {"name": "Test User", "registered_on": "2021-01-01 00:00:00.000000000"}
        mock_account.gerrit.get.return_value = detail
        result = mock_account.get_detail()
        assert "name" in result

    def test_get_name(self, mock_account):
        mock_account.gerrit.get.return_value = "Test User"
        result = mock_account.get_name()
        assert result == "Test User"

    def test_set_name(self, mock_account):
        mock_account.gerrit.put.return_value = "New Name"
        input_ = {"name": "New Name"}
        result = mock_account.set_name(input_)
        mock_account.gerrit.put.assert_called()

    def test_delete_name(self, mock_account):
        mock_account.delete_name()
        mock_account.gerrit.delete.assert_called_once()

    def test_get_status(self, mock_account):
        mock_account.gerrit.get.return_value = "working"
        result = mock_account.get_status()
        assert result == "working"

    def test_set_status(self, mock_account):
        mock_account.gerrit.put.return_value = "active"
        mock_account.set_status("active")
        mock_account.gerrit.put.assert_called()

    def test_get_active(self, mock_account):
        mock_account.gerrit.get.return_value = "ok"
        result = mock_account.get_active()
        assert result == "ok"

    def test_set_active(self, mock_account):
        mock_account.set_active()
        mock_account.gerrit.put.assert_called()

    def test_delete_active(self, mock_account):
        mock_account.delete_active()
        mock_account.gerrit.delete.assert_called()

    def test_set_displayname(self, mock_account):
        mock_account.gerrit.put.return_value = {"display_name": "Kevin"}
        input_ = {"display_name": "Kevin"}
        mock_account.set_displayname(input_)
        mock_account.gerrit.put.assert_called()

    def test_get_displayname(self, mock_account):
        mock_account.gerrit.get.return_value = "Kevin"
        result = mock_account.get_displayname()
        assert result == "Kevin"
        mock_account.gerrit.get.assert_called()

    def test_set_username(self, mock_account):
        mock_account.gerrit.put.return_value = {"username": "newuser"}
        mock_account.set_username({"username": "newuser"})
        mock_account.gerrit.put.assert_called()

    def test_get_username(self, mock_account):
        mock_account.gerrit.get.return_value = "testuser"
        result = mock_account.get_username()
        assert result == "testuser"
        mock_account.gerrit.get.assert_called()

    def test_set_http_password(self, mock_account):
        mock_account.gerrit.put.return_value = "password123"
        mock_account.set_http_password({"generate": True})
        mock_account.gerrit.put.assert_called()

    def test_delete_http_password(self, mock_account):
        mock_account.delete_http_password()
        mock_account.gerrit.delete.assert_called()

    def test_list_capabilities(self, mock_account):
        mock_account.gerrit.get.return_value = {"queryLimit": {"min": 0, "max": 500}}
        result = mock_account.list_capabilities()
        assert "queryLimit" in result

    def test_check_capability(self, mock_account):
        mock_account.gerrit.get.return_value = "ok"
        result = mock_account.check_capability("account-deleteOwnAccount")
        assert result == "ok"

    def test_get_groups(self, mock_account):
        mock_account.gerrit.get.return_value = [{"id": "abc", "name": "Developers"}]
        groups = mock_account.groups
        assert len(groups) > 0

    def test_get_avatar(self, mock_account):
        mock_account.gerrit.get.return_value = b"\x89PNG\r\n..."
        avatar = mock_account.get_avatar()
        assert isinstance(avatar, bytes)

    def test_get_avatar_change_url(self, mock_account):
        mock_account.gerrit.get.return_value = "http://www.gravatar.com"
        url = mock_account.get_avatar_change_url()
        assert url == "http://www.gravatar.com"

    def test_get_user_preferences(self, mock_account):
        prefs = {"changes_per_page": 25, "date_format": "STD"}
        mock_account.gerrit.get.return_value = prefs
        result = mock_account.get_user_preferences()
        assert "changes_per_page" in result

    def test_set_user_preferences(self, mock_account):
        prefs = {"changes_per_page": 50}
        mock_account.gerrit.put.return_value = prefs
        result = mock_account.set_user_preferences(prefs)
        mock_account.gerrit.put.assert_called()

    def test_get_diff_preferences(self, mock_account):
        prefs = {"line_length": 100, "tab_size": 8}
        mock_account.gerrit.get.return_value = prefs
        result = mock_account.get_diff_preferences()
        assert "line_length" in result

    def test_set_diff_preferences(self, mock_account):
        prefs = {"line_length": 120}
        mock_account.gerrit.put.return_value = prefs
        result = mock_account.set_diff_preferences(prefs)
        mock_account.gerrit.put.assert_called()

    def test_get_edit_preferences(self, mock_account):
        prefs = {"line_length": 100, "tab_size": 4}
        mock_account.gerrit.get.return_value = prefs
        result = mock_account.get_edit_preferences()
        assert "line_length" in result

    def test_set_edit_preferences(self, mock_account):
        prefs = {"line_length": 100}
        mock_account.gerrit.put.return_value = prefs
        result = mock_account.set_edit_preferences(prefs)
        mock_account.gerrit.put.assert_called()

    def test_get_watched_projects(self, mock_account):
        mock_account.gerrit.get.return_value = [{"project": "myProject"}]
        result = mock_account.get_watched_projects()
        assert len(result) >= 0

    def test_modify_watched_projects(self, mock_account):
        mock_account.gerrit.post.return_value = [{"project": "myProject"}]
        input_ = [{"project": "myProject", "notify_new_changes": True}]
        result = mock_account.modify_watched_projects(input_)
        mock_account.gerrit.post.assert_called()

    def test_delete_watched_projects(self, mock_account):
        input_ = [{"project": "myProject"}]
        mock_account.delete_watched_projects(input_)
        mock_account.gerrit.post.assert_called()


# ---------------------------------------------------------------------------
# GerritAccountEmails
# ---------------------------------------------------------------------------

class TestGerritAccountEmails:

    def test_list_emails(self, mock_account):
        emails_data = [{"email": "test@example.com", "preferred": True}]
        mock_account.gerrit.get.return_value = emails_data
        emails = mock_account.emails.list()
        assert len(emails) >= 1

    def test_get_email(self, mock_account):
        email_data = {"email": "test@example.com", "preferred": True}
        mock_account.gerrit.get.return_value = email_data
        email = mock_account.emails.get("test@example.com")
        assert email.to_dict().get("email") == "test@example.com"

    def test_get_email_not_found(self, mock_account):
        response_mock = MagicMock()
        response_mock.status_code = 404
        http_error = requests.exceptions.HTTPError(response=response_mock)
        mock_account.gerrit.get.side_effect = http_error

        from gerrit.utils.exceptions import AccountEmailNotFoundError
        with pytest.raises(AccountEmailNotFoundError):
            mock_account.emails.get("nobody@example.com")

    def test_create_email(self, mock_account):
        # When email already exists, create() should raise AccountEmailAlreadyExistsError
        email_data = {"email": "test@example.com", "preferred": True}
        mock_account.gerrit.get.return_value = email_data

        from gerrit.utils.exceptions import AccountEmailAlreadyExistsError
        with pytest.raises(AccountEmailAlreadyExistsError):
            mock_account.emails.create("test@example.com")

    def test_create_email_with_input(self, mock_account):
        # When email doesn't exist, create() with EmailInput should call PUT with body
        email_data = {"email": "new@example.com", "preferred": False}
        response_mock = MagicMock()
        response_mock.status_code = 404
        http_error = requests.exceptions.HTTPError(response=response_mock)
        # 1st get: 404 (existence check); 2nd get: returns data; 3rd get: GerritAccountEmail.poll()
        mock_account.gerrit.get.side_effect = [http_error, email_data, email_data]
        input_ = {"email": "new@example.com", "preferred": False, "no_confirmation": True}
        mock_account.emails.create("new@example.com", input_)
        mock_account.gerrit.put.assert_called_once()
        call_args = mock_account.gerrit.put.call_args
        assert call_args[1]["json"] == input_


# ---------------------------------------------------------------------------
# GerritAccountSSHKeys & GerritAccountGPGKeys
# ---------------------------------------------------------------------------

class TestGerritAccountSSHKeys:

    def test_list_ssh_keys(self, mock_account):
        mock_account.gerrit.get.return_value = [{"seq": 1, "ssh_public_key": "ssh-rsa AAAA..."}]
        ssh_keys = mock_account.ssh_keys.list()
        assert len(ssh_keys) >= 0

    def test_add_ssh_key(self, mock_account):
        mock_account.gerrit.post.return_value = {"seq": 2, "ssh_public_key": "ssh-rsa BBBB..."}
        mock_account.ssh_keys.add("ssh-rsa BBBB...")
        mock_account.gerrit.post.assert_called_once()

    def test_get_ssh_key(self, mock_account):
        key_data = {"seq": 1, "ssh_public_key": "ssh-rsa AAAA...", "valid": True}
        mock_account.gerrit.get.return_value = key_data
        key = mock_account.ssh_keys.get(1)
        assert key.to_dict().get("seq") == 1

    def test_get_ssh_key_not_found(self, mock_account):
        response_mock = MagicMock()
        response_mock.status_code = 404
        mock_account.gerrit.get.side_effect = requests.exceptions.HTTPError(
            response=response_mock
        )
        from gerrit.utils.exceptions import SSHKeyNotFoundError
        with pytest.raises(SSHKeyNotFoundError):
            mock_account.ssh_keys.get(999)

    def test_delete_ssh_key(self, mock_account):
        key_data = {"seq": 1, "ssh_public_key": "ssh-rsa AAAA...", "valid": True}
        mock_account.gerrit.get.return_value = key_data
        mock_account.ssh_keys.delete(1)
        mock_account.gerrit.delete.assert_called()


class TestGerritAccountGPGKeys:

    def test_list_gpg_keys(self, mock_account):
        mock_account.gerrit.get.return_value = {}
        gpg_keys = mock_account.gpg_keys.list()
        assert isinstance(gpg_keys, list)

    def test_add_gpg_keys(self, mock_account):
        mock_account.gerrit.post.return_value = {"abc123": {"fingerprint": "abc123"}}
        mock_account.gpg_keys.modify({"add": ["-----BEGIN PGP PUBLIC KEY BLOCK-----"], "delete": []})
        mock_account.gerrit.post.assert_called_once()

    def test_get_gpg_key(self, mock_account):
        key_data = {"id": "abc123", "fingerprint": "abc123"}
        mock_account.gerrit.get.return_value = key_data
        key = mock_account.gpg_keys.get("abc123")
        assert key.to_dict().get("id") == "abc123"

    def test_get_gpg_key_not_found(self, mock_account):
        response_mock = MagicMock()
        response_mock.status_code = 404
        mock_account.gerrit.get.side_effect = requests.exceptions.HTTPError(
            response=response_mock
        )
        from gerrit.utils.exceptions import GPGKeyNotFoundError
        with pytest.raises(GPGKeyNotFoundError):
            mock_account.gpg_keys.get("nonexistent")

    def test_delete_gpg_key(self, mock_account):
        key_data = {"id": "abc123", "fingerprint": "abc123"}
        mock_account.gerrit.get.return_value = key_data
        mock_account.gpg_keys.delete("abc123")
        mock_account.gerrit.delete.assert_called()

