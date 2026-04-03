#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Unit tests for gerrit.base.GerritClient.
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import requests


BASE_URL = "http://localhost:8080"


@pytest.fixture
def basic_client():
    """GerritClient with username+password auth and mocked requests.Session."""
    with patch("gerrit.base.requests.Session") as MockSession:
        mock_session = MagicMock()
        MockSession.return_value = mock_session

        from gerrit.base import GerritClient
        client = GerritClient(
            base_url=BASE_URL,
            username="admin",
            password="secret",
        )
    return client


@pytest.fixture
def anon_client():
    """GerritClient with no auth credentials."""
    with patch("gerrit.base.requests.Session") as MockSession:
        mock_session = MagicMock()
        mock_session.auth = None
        MockSession.return_value = mock_session

        from gerrit.base import GerritClient
        client = GerritClient(base_url=BASE_URL)
    return client


# ===========================================================================
# GerritClient initialisation
# ===========================================================================

class TestGerritClientInit:

    def test_auth_sets_session_auth(self):
        with patch("gerrit.base.requests.Session") as MockSession:
            mock_session = MagicMock()
            MockSession.return_value = mock_session

            from gerrit.base import GerritClient
            GerritClient(base_url=BASE_URL, username="u", password="p")
            assert mock_session.auth == ("u", "p")

    def test_no_auth_leaves_session_auth_unset(self):
        with patch("gerrit.base.requests.Session") as MockSession:
            mock_session = MagicMock()
            mock_session.auth = None
            MockSession.return_value = mock_session

            from gerrit.base import GerritClient
            client = GerritClient(base_url=BASE_URL)
            assert client.auth_suffix == ""

    def test_ssl_verify_applied(self):
        with patch("gerrit.base.requests.Session") as MockSession:
            mock_session = MagicMock()
            MockSession.return_value = mock_session

            from gerrit.base import GerritClient
            GerritClient(base_url=BASE_URL, ssl_verify="/path/to/ca.pem")
            assert mock_session.verify == "/path/to/ca.pem"

    def test_cert_applied(self):
        with patch("gerrit.base.requests.Session") as MockSession:
            mock_session = MagicMock()
            MockSession.return_value = mock_session

            from gerrit.base import GerritClient
            GerritClient(base_url=BASE_URL, cert=("/path/cert.pem", "/path/key.pem"))
            assert mock_session.cert == ("/path/cert.pem", "/path/key.pem")

    def test_cookies_applied(self):
        with patch("gerrit.base.requests.Session") as MockSession:
            mock_session = MagicMock()
            MockSession.return_value = mock_session

            from gerrit.base import GerritClient
            GerritClient(base_url=BASE_URL, cookies={"session": "abc"})
            mock_session.cookies.update.assert_called_once_with({"session": "abc"})

    def test_cookie_jar_applied(self):
        with patch("gerrit.base.requests.Session") as MockSession:
            mock_session = MagicMock()
            MockSession.return_value = mock_session

            from gerrit.base import GerritClient
            jar = MagicMock()
            GerritClient(base_url=BASE_URL, cookie_jar=jar)
            assert mock_session.cookies == jar

    def test_max_retries_mounts_adapters(self):
        with patch("gerrit.base.requests.Session") as MockSession, \
             patch("gerrit.base.HTTPAdapter") as MockAdapter:
            mock_session = MagicMock()
            MockSession.return_value = mock_session
            mock_adapter = MagicMock()
            MockAdapter.return_value = mock_adapter

            from gerrit.base import GerritClient
            GerritClient(base_url=BASE_URL, max_retries=3)
            mock_session.mount.assert_any_call("http://", mock_adapter)
            mock_session.mount.assert_any_call("https://", mock_adapter)

    def test_provided_session_used(self):
        provided_session = MagicMock()
        provided_session.auth = ("u", "p")

        from gerrit.base import GerritClient
        client = GerritClient(base_url=BASE_URL, session=provided_session)
        assert client.session is provided_session

    def test_auth_suffix_set_when_auth_present(self):
        with patch("gerrit.base.requests.Session") as MockSession:
            mock_session = MagicMock()
            mock_session.auth = ("u", "p")
            MockSession.return_value = mock_session

            from gerrit.base import GerritClient
            client = GerritClient(
                base_url=BASE_URL, username="u", password="p", auth_suffix="/a"
            )
            assert client.auth_suffix == "/a"


# ===========================================================================
# get_endpoint_url
# ===========================================================================

class TestGetEndpointUrl:

    def test_with_auth(self, basic_client):
        url = basic_client.get_endpoint_url("/projects/")
        assert url == f"{BASE_URL}/a/projects/"

    def test_without_auth(self, anon_client):
        url = anon_client.get_endpoint_url("/projects/")
        assert url == f"{BASE_URL}/projects/"


# ===========================================================================
# Properties (access, config, projects, changes, accounts, groups, plugins)
# ===========================================================================

class TestGerritClientProperties:

    def test_access_property(self, basic_client):
        from gerrit.access import GerritAccess
        assert isinstance(basic_client.access, GerritAccess)

    def test_config_property(self, basic_client):
        from gerrit.config.config import GerritConfig
        assert isinstance(basic_client.config, GerritConfig)

    def test_projects_property(self, basic_client):
        from gerrit.projects.projects import GerritProjects
        assert isinstance(basic_client.projects, GerritProjects)

    def test_changes_property(self, basic_client):
        from gerrit.changes.changes import GerritChanges
        assert isinstance(basic_client.changes, GerritChanges)

    def test_accounts_property(self, basic_client):
        from gerrit.accounts.accounts import GerritAccounts
        assert isinstance(basic_client.accounts, GerritAccounts)

    def test_groups_property(self, basic_client):
        from gerrit.groups.groups import GerritGroups
        assert isinstance(basic_client.groups, GerritGroups)

    def test_plugins_property(self, basic_client):
        from gerrit.plugins.plugins import GerritPlugins
        assert isinstance(basic_client.plugins, GerritPlugins)


# ===========================================================================
# HTTP helper methods (get/post/put/delete)
# ===========================================================================

class TestGerritClientHTTPHelpers:

    def _setup_requester(self, client, response_data):
        """Mock requester.get/post/put/delete to return a faked response."""
        import json as _json
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.encoding = "utf-8"
        mock_response.content = _json.dumps(response_data).encode("utf-8")
        return mock_response

    def test_get(self, basic_client):
        resp = self._setup_requester(basic_client, {"ok": True})
        basic_client.requester.get = MagicMock(return_value=resp)
        result = basic_client.get("/projects/")
        assert result == {"ok": True}

    def test_post(self, basic_client):
        resp = self._setup_requester(basic_client, {"created": True})
        basic_client.requester.post = MagicMock(return_value=resp)
        result = basic_client.post("/changes/", json={"project": "test"})
        assert result == {"created": True}

    def test_put(self, basic_client):
        resp = self._setup_requester(basic_client, {"updated": True})
        basic_client.requester.put = MagicMock(return_value=resp)
        result = basic_client.put("/projects/test/config", json={})
        assert result == {"updated": True}

    def test_delete(self, basic_client):
        resp = MagicMock()
        resp.headers = {"content-type": "text/plain"}
        resp.encoding = "utf-8"
        resp.content = b""
        basic_client.requester.delete = MagicMock(return_value=resp)
        basic_client.delete("/projects/test")
        basic_client.requester.delete.assert_called_once()


# ===========================================================================
# version and server properties (delegate to config)
# ===========================================================================

class TestGerritClientVersionServer:

    def test_version(self, basic_client):
        with patch.object(type(basic_client), "config", new_callable=PropertyMock) as mock_config_prop:
            mock_config = MagicMock()
            mock_config.get_version.return_value = "3.5.0"
            mock_config_prop.return_value = mock_config

            assert basic_client.version == "3.5.0"

    def test_server(self, basic_client):
        with patch.object(type(basic_client), "config", new_callable=PropertyMock) as mock_config_prop:
            mock_config = MagicMock()
            mock_config.get_server_info.return_value = {"auth": {}}
            mock_config_prop.return_value = mock_config

            assert basic_client.server == {"auth": {}}


# ===========================================================================
# get_password_from_netrc_file
# ===========================================================================

class TestGetPasswordFromNetrc:

    def test_host_found_in_netrc(self, basic_client):
        with patch("gerrit.base.netrc.netrc") as MockNetrc:
            mock_netrc = MagicMock()
            mock_netrc.authenticators.return_value = ("user", "account", "password123")
            MockNetrc.return_value = mock_netrc

            basic_client._base_url = "https://gerrit.example.com/r"
            password = basic_client.get_password_from_netrc_file()
            mock_netrc.authenticators.assert_called_once_with("gerrit.example.com")
            assert password == "password123"

    def test_host_not_found_raises(self, basic_client):
        with patch("gerrit.base.netrc.netrc") as MockNetrc:
            mock_netrc = MagicMock()
            mock_netrc.authenticators.return_value = None
            MockNetrc.return_value = mock_netrc

            basic_client._base_url = "unknown.host.com"
            with pytest.raises(ValueError, match="not found in netrc file"):
                basic_client.get_password_from_netrc_file()

    def test_host_without_password_raises(self, basic_client):
        with patch("gerrit.base.netrc.netrc") as MockNetrc:
            mock_netrc = MagicMock()
            mock_netrc.authenticators.return_value = ("user", "account", None)
            MockNetrc.return_value = mock_netrc

            basic_client._base_url = "https://gerrit.example.com"
            with pytest.raises(ValueError, match="not found in netrc file"):
                basic_client.get_password_from_netrc_file()
