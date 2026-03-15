#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
"""
Unit tests for gerrit.access — all HTTP calls are mocked.
"""
import logging
import pytest

logger = logging.getLogger(__name__)

ACCESS_DATA = {
    "All-Projects": {
        "revision": "edd453d18e08640e67a8c9a150cec998ed0ac9aa",
        "inherits_from": None,
        "is_owner": True,
        "can_upload": True,
        "can_add": True,
        "config_visible": True,
        "local": {
            "refs/*": {
                "permissions": {
                    "read": {
                        "rules": {
                            "global:Anonymous-Users": {"action": "ALLOW", "force": False}
                        }
                    }
                }
            }
        },
        "groups": {}
    }
}


class TestGerritAccess:

    def test_list_access_rights(self, mock_gerrit):
        mock_gerrit.get.return_value = ACCESS_DATA

        from gerrit.access import GerritAccess
        access = GerritAccess(gerrit=mock_gerrit)
        result = access.list(projects=["All-Projects"])

        mock_gerrit.get.assert_called_once()
        call_args = mock_gerrit.get.call_args
        assert "/access/" in call_args[0][0]
        assert result == ACCESS_DATA

    def test_list_access_rights_multiple_projects(self, mock_gerrit):
        mock_gerrit.get.return_value = ACCESS_DATA

        from gerrit.access import GerritAccess
        access = GerritAccess(gerrit=mock_gerrit)
        result = access.list(projects=["All-Projects", "myProject"])

        mock_gerrit.get.assert_called_once()
        call_args = mock_gerrit.get.call_args
        # params should be a list of tuples for repeated keys
        params = call_args[1]["params"]
        assert len(params) == 2
        assert all(k == "project" for k, _ in params)

    def test_create_access_rights_change(self, mock_gerrit):
        change_info = {
            "id": "All-Projects~refs%2Fmeta%2Fconfig~Ied702f97660e16e9ac3f5d2a52d5e38a23e62e6e",
            "project": "All-Projects",
            "branch": "refs/meta/config",
            "status": "NEW",
        }
        mock_gerrit.post.return_value = change_info

        from gerrit.access import GerritAccess
        access = GerritAccess(gerrit=mock_gerrit)
        input_ = {
            "project": "All-Projects",
            "subject": "Update access rights",
            "add": {
                "refs/heads/*": {
                    "permissions": {
                        "read": {
                            "rules": {
                                "global:Anonymous-Users": {"action": "ALLOW"}
                            }
                        }
                    }
                }
            },
        }
        result = access.create_change(input_)

        mock_gerrit.post.assert_called_once()
        call_args = mock_gerrit.post.call_args
        assert "/access/" in call_args[0][0]
        assert call_args[1]["json"] == input_
        assert result["project"] == "All-Projects"

    def test_access_property_on_client(self, mock_gerrit):
        """GerritClient.access should return a GerritAccess instance."""
        from gerrit import GerritClient
        from gerrit.access import GerritAccess

        # Use the actual GerritClient constructor with a mock session
        from unittest.mock import patch, MagicMock
        with patch("requests.Session") as mock_session_cls:
            mock_session_cls.return_value = MagicMock()
            client = GerritClient(
                base_url="http://localhost",
                username="admin",
                password="secret",
            )
        assert isinstance(client.access, GerritAccess)
