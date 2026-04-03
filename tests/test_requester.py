#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Unit tests for gerrit.utils.requester and gerrit.utils.common.
"""
import json
import pytest
from unittest.mock import MagicMock, patch

from gerrit.utils.requester import Requester
from gerrit.utils.exceptions import (
    ValidationError,
    UnauthorizedError,
    AuthError,
    NotAllowedError,
    ConflictError,
    ClientError,
    ServerError,
)
from gerrit.utils.common import strip_trailing_slash, decode_response, params_creator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_response(status_code, reason="OK", url="http://example.com/", body=b"", content_type="application/json", encoding="utf-8"):
    """Build a minimal mock Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.reason = reason
    resp.url = url
    resp.content = body
    resp.encoding = encoding
    resp.headers = {"content-type": content_type}
    resp.raise_for_status = MagicMock()
    return resp


def _make_requester(base_url="http://example.com"):
    session = MagicMock()
    return Requester(base_url=base_url, session=session, timeout=5)


# ===========================================================================
# strip_trailing_slash
# ===========================================================================

class TestStripTrailingSlash:

    def test_no_slash(self):
        assert strip_trailing_slash("http://example.com") == "http://example.com"

    def test_single_slash(self):
        assert strip_trailing_slash("http://example.com/") == "http://example.com"

    def test_multiple_slashes(self):
        assert strip_trailing_slash("http://example.com///") == "http://example.com"

    def test_empty_string(self):
        assert strip_trailing_slash("") == ""


# ===========================================================================
# decode_response
# ===========================================================================

class TestDecodeResponse:

    def test_empty_content(self):
        resp = _make_response(200, body=b"   ", encoding="utf-8")
        result = decode_response(resp)
        assert result == ""

    def test_plain_text_content(self):
        resp = _make_response(200, body=b"hello", content_type="text/plain", encoding="utf-8")
        result = decode_response(resp)
        assert result == "hello"

    def test_json_with_magic_prefix(self):
        data = {"key": "value"}
        body = (")]}'\n" + json.dumps(data)).encode("utf-8")
        resp = _make_response(200, body=body, encoding="utf-8")
        result = decode_response(resp)
        assert result == data

    def test_json_without_magic_prefix(self):
        data = {"key": "value"}
        body = json.dumps(data).encode("utf-8")
        resp = _make_response(200, body=body, encoding="utf-8")
        result = decode_response(resp)
        assert result == data

    def test_invalid_json_raises(self):
        body = b"not-valid-json"
        resp = _make_response(200, body=body, encoding="utf-8")
        with pytest.raises(ValueError, match="Invalid json content"):
            decode_response(resp)

    def test_no_encoding_falls_back_to_utf8(self):
        data = {"k": 1}
        body = json.dumps(data).encode("utf-8")
        resp = _make_response(200, body=body, encoding=None)
        result = decode_response(resp)
        assert result == data


# ===========================================================================
# params_creator
# ===========================================================================

class TestParamsCreator:

    def test_no_dispatcher(self):
        result = params_creator((("n", 10), ("s", 0)), {"match": "m", "regex": "r"}, None)
        assert result == {"n": 10, "s": 0}

    def test_with_empty_dispatcher(self):
        result = params_creator((("n", 10),), {"match": "m", "regex": "r"}, {})
        assert result == {"n": 10}

    def test_with_match_dispatcher(self):
        result = params_creator(
            (("n", 25), ("s", 0)),
            {"match": "m", "regex": "r"},
            {"match": "myproject"},
        )
        assert result["m"] == "myproject"
        assert result["n"] == 25

    def test_with_regex_dispatcher(self):
        result = params_creator(
            (("n", 25),),
            {"match": "m", "regex": "r"},
            {"regex": "my.*"},
        )
        assert result["r"] == "my.*"

    def test_invalid_dispatcher_key_raises(self):
        with pytest.raises(ValueError):
            params_creator(
                (("n", 25),),
                {"match": "m", "regex": "r"},
                {"unknown": "value"},
            )

    def test_invalid_dispatcher_key_with_single_pattern_type(self):
        with pytest.raises(ValueError, match="Pattern types can be either match"):
            params_creator(
                (("n", 25),),
                {"match": "m"},
                {"unknown": "value"},
            )

    def test_none_values_omitted(self):
        result = params_creator((("n", None), ("s", 0)), {"match": "m"}, None)
        assert "n" not in result
        assert result["s"] == 0


# ===========================================================================
# Requester._update_url_scheme
# ===========================================================================

class TestRequesterUpdateUrlScheme:

    def test_same_scheme_unchanged(self):
        req = _make_requester("http://example.com")
        url = "http://example.com/path"
        assert req._update_url_scheme(url) == url

    def test_scheme_replaced(self):
        req = _make_requester("https://example.com")
        url = "http://example.com/path"
        result = req._update_url_scheme(url)
        assert result.startswith("https://")

    def test_no_base_scheme(self):
        req = Requester(session=MagicMock(), timeout=5)
        url = "http://example.com/path"
        assert req._update_url_scheme(url) == url


# ===========================================================================
# Requester.get_request_dict
# ===========================================================================

class TestRequesterGetRequestDict:

    def test_basic(self):
        req = _make_requester()
        d = req.get_request_dict()
        assert d["timeout"] == 5

    def test_with_dict_params(self):
        req = _make_requester()
        d = req.get_request_dict(params={"k": "v"})
        assert d["params"] == {"k": "v"}

    def test_with_list_params(self):
        req = _make_requester()
        d = req.get_request_dict(params=[("k", "v")])
        assert d["params"] == [("k", "v")]

    def test_invalid_params_raises(self):
        req = _make_requester()
        with pytest.raises(ValueError, match="Params must be a dict"):
            req.get_request_dict(params="invalid")

    def test_with_headers(self):
        req = _make_requester()
        d = req.get_request_dict(headers={"X-Custom": "1"})
        assert d["headers"] == {"X-Custom": "1"}

    def test_invalid_headers_raises(self):
        req = _make_requester()
        with pytest.raises(ValueError, match="headers must be a dict"):
            req.get_request_dict(headers="invalid")

    def test_with_auth_cookie(self):
        req = _make_requester()
        req.AUTH_COOKIE = "session=abc"
        d = req.get_request_dict()
        assert d["headers"]["Cookie"] == "session=abc"

    def test_auth_cookie_merges_with_existing_headers(self):
        req = _make_requester()
        req.AUTH_COOKIE = "session=abc"
        d = req.get_request_dict(headers={"X-Custom": "1"})
        assert d["headers"]["Cookie"] == "session=abc"
        assert d["headers"]["X-Custom"] == "1"

    def test_data_and_json_together_raises(self):
        req = _make_requester()
        with pytest.raises(ValueError, match="Cannot use data and json together"):
            req.get_request_dict(data="raw", json={"k": "v"})

    def test_with_data(self):
        req = _make_requester()
        d = req.get_request_dict(data="raw body")
        assert d["data"] == "raw body"

    def test_with_json(self):
        req = _make_requester()
        d = req.get_request_dict(json={"k": "v"})
        assert d["json"] == {"k": "v"}


# ===========================================================================
# Requester HTTP methods
# ===========================================================================

class TestRequesterHTTPMethods:

    def _make_ok_response(self):
        resp = _make_response(200, body=b'{"ok": true}')
        return resp

    def test_get(self):
        req = _make_requester()
        req.session.get.return_value = self._make_ok_response()
        resp = req.get("http://example.com/endpoint")
        req.session.get.assert_called_once()
        assert resp.status_code == 200

    def test_get_with_raise_for_status_false(self):
        req = _make_requester()
        bad_resp = _make_response(500, reason="Internal Server Error")
        req.session.get.return_value = bad_resp
        resp = req.get("http://example.com/endpoint", raise_for_status=False)
        assert resp.status_code == 500

    def test_post(self):
        req = _make_requester()
        req.session.post.return_value = self._make_ok_response()
        resp = req.post("http://example.com/endpoint", json={"key": "val"})
        req.session.post.assert_called_once()
        assert resp.status_code == 200

    def test_post_with_raise_for_status_false(self):
        req = _make_requester()
        bad_resp = _make_response(400, reason="Bad Request")
        req.session.post.return_value = bad_resp
        resp = req.post("http://example.com/endpoint", raise_for_status=False)
        assert resp.status_code == 400

    def test_put(self):
        req = _make_requester()
        req.session.put.return_value = self._make_ok_response()
        resp = req.put("http://example.com/endpoint")
        req.session.put.assert_called_once()
        assert resp.status_code == 200

    def test_put_with_raise_for_status_false(self):
        req = _make_requester()
        bad_resp = _make_response(409, reason="Conflict")
        req.session.put.return_value = bad_resp
        resp = req.put("http://example.com/endpoint", raise_for_status=False)
        assert resp.status_code == 409

    def test_delete(self):
        req = _make_requester()
        req.session.delete.return_value = self._make_ok_response()
        resp = req.delete("http://example.com/endpoint")
        req.session.delete.assert_called_once()
        assert resp.status_code == 200

    def test_delete_with_raise_for_status_false(self):
        req = _make_requester()
        bad_resp = _make_response(403, reason="Forbidden")
        req.session.delete.return_value = bad_resp
        resp = req.delete("http://example.com/endpoint", raise_for_status=False)
        assert resp.status_code == 403


# ===========================================================================
# Requester.confirm_status
# ===========================================================================

class TestConfirmStatus:

    def test_200_ok(self):
        resp = _make_response(200)
        Requester.confirm_status(resp)  # should not raise

    def test_400_raises_validation_error(self):
        resp = _make_response(400, reason="Bad Request")
        with pytest.raises(ValidationError):
            Requester.confirm_status(resp)

    def test_401_raises_unauthorized(self):
        resp = _make_response(401, reason="Unauthorized")
        with pytest.raises(UnauthorizedError):
            Requester.confirm_status(resp)

    def test_403_raises_auth_error(self):
        resp = _make_response(403, reason="Forbidden")
        with pytest.raises(AuthError):
            Requester.confirm_status(resp)

    def test_404_calls_raise_for_status(self):
        resp = _make_response(404, reason="Not Found")
        resp.raise_for_status.side_effect = Exception("404")
        with pytest.raises(Exception, match="404"):
            Requester.confirm_status(resp)
        resp.raise_for_status.assert_called_once()

    def test_405_raises_not_allowed(self):
        resp = _make_response(405, reason="Method Not Allowed")
        with pytest.raises(NotAllowedError):
            Requester.confirm_status(resp)

    def test_409_raises_conflict(self):
        resp = _make_response(409, reason="Conflict")
        with pytest.raises(ConflictError):
            Requester.confirm_status(resp)

    def test_other_4xx_raises_client_error(self):
        resp = _make_response(422, reason="Unprocessable Entity")
        with pytest.raises(ClientError):
            Requester.confirm_status(resp)

    def test_5xx_raises_server_error(self):
        resp = _make_response(500, reason="Internal Server Error")
        with pytest.raises(ServerError):
            Requester.confirm_status(resp)

    def test_reason_bytes_utf8(self):
        resp = _make_response(400, reason=b"Bad Request")
        with pytest.raises(ValidationError):
            Requester.confirm_status(resp)

    def test_reason_bytes_iso(self):
        # Byte string that can't be decoded as utf-8 but can be as iso-8859-1
        reason_bytes = b"Bad \xe9"
        resp = _make_response(400, reason=reason_bytes)
        with pytest.raises(ValidationError) as exc_info:
            Requester.confirm_status(resp)
        # The fallback iso-8859-1 decoding should produce a non-empty reason in the message
        assert "Bad" in str(exc_info.value)
