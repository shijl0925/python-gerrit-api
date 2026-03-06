#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
"""
Unit tests for gitiles.GitilesClient — all HTTP calls are mocked.
"""
import base64
import logging
import pytest
from unittest.mock import MagicMock, patch

logger = logging.getLogger(__name__)

COMMIT_INFO = {
    "commit": "baaf2895e0732228c84a07620fffe57e4ff47f03",
    "tree": "abc123",
    "parents": ["parent_sha"],
    "author": {"name": "Test Author", "email": "author@example.com", "time": "1000000 +0000"},
    "committer": {"name": "Test Committer", "email": "committer@example.com", "time": "1000000 +0000"},
    "message": "Test commit message",
}

COMMITS_RESPONSE = {
    "next": "next_page_token",
    "log": [COMMIT_INFO],
}

FILE_CONTENT = base64.b64encode(b"#!/bin/bash\necho hello\n").decode("utf-8")


@pytest.fixture
def mock_gitiles():
    """Create a GitilesClient with a mocked requester for unit testing."""
    from gitiles import GitilesClient

    client = GitilesClient(base_url="http://localhost:8080")

    # Mock the requester's get method to avoid real HTTP calls
    mock_response = MagicMock()
    mock_response.headers = {"content-type": "application/json"}
    mock_response.encoding = "utf-8"
    mock_response.content = b")"  # will be overridden per test

    client.requester = MagicMock()
    return client


class TestGitilesClient:

    def test_commit(self, mock_gitiles):
        """Test retrieving a specific commit."""
        from gerrit.utils.common import decode_response

        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.encoding = "utf-8"
        # Gerrit JSON response with magic prefix
        import json
        body = ")]}'\n" + json.dumps(COMMIT_INFO)
        mock_response.content = body.encode("utf-8")

        mock_gitiles.requester.get.return_value = mock_response

        result = mock_gitiles.commit("gitiles", commit="baaf2895e0732228c84a07620fffe57e4ff47f03")
        assert "commit" in result
        assert "author" in result
        assert "message" in result

    def test_commits(self, mock_gitiles):
        """Test querying commit history."""
        import json
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.encoding = "utf-8"
        body = ")]}'\n" + json.dumps(COMMITS_RESPONSE)
        mock_response.content = body.encode("utf-8")

        mock_gitiles.requester.get.return_value = mock_response

        result = mock_gitiles.commits(
            "gitiles",
            "refs/heads/master",
            start="baaf2895e0732228c84a07620fffe57e4ff47f03",
        )
        assert "next" in result
        assert "log" in result
        assert len(result.get("log")) > 0

    def test_download_file(self, mock_gitiles):
        """Test downloading raw file content."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.encoding = "utf-8"
        mock_response.content = FILE_CONTENT.encode("utf-8")

        mock_gitiles.requester.get.return_value = mock_response

        result = mock_gitiles.download_file(
            "buck", "refs/heads/master", "scripts/install.sh"
        )
        assert len(result) > 0

    def test_download_file_decoded(self, mock_gitiles):
        """Test downloading and decoding file content."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.encoding = "utf-8"
        mock_response.content = FILE_CONTENT.encode("utf-8")

        mock_gitiles.requester.get.return_value = mock_response

        result = mock_gitiles.download_file(
            "buck", "refs/heads/master", "scripts/install.sh", decode=True
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_endpoint_url(self, mock_gitiles):
        """Test URL construction."""
        url = mock_gitiles.get_endpoint_url("/gitiles/+/abc123")
        assert url == "http://localhost:8080/gitiles/+/abc123"

