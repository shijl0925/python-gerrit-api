#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from requests import Session
from requests.adapters import HTTPAdapter
import six.moves.urllib.parse as urlparse
from gerrit.utils.exceptions import (
    NotAllowedError,
    ValidationError,
    AuthError,
    UnauthorizedError,
    NotFoundError,
    ConflictError,
    ClientError,
    ServerError,
)


class Requester(object):

    """
    A class which carries out HTTP requests. You can replace this
    class with one of your own implementation if you require some other
    way to access Gerrit.
    This default class can handle simple authentication only.
    """

    VALID_STATUS_CODES = [
        200,
    ]
    AUTH_COOKIE = None

    def __init__(self, **kwargs):
        """
        :param kwargs:
        """
        timeout = 10
        base_url = kwargs.get('base_url')
        self.base_scheme = urlparse.urlsplit(base_url).scheme if base_url else None
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")
        self.ssl_verify = kwargs.get("ssl_verify")
        self.cert = kwargs.get("cert")
        self.timeout = kwargs.get("timeout", timeout)
        self.session = Session()

        self.max_retries = kwargs.get("max_retries")
        if self.max_retries is not None:
            retry_adapter = HTTPAdapter(max_retries=self.max_retries)
            self.session.mount("http://", retry_adapter)
            self.session.mount("https://", retry_adapter)

    def _update_url_scheme(self, url):
        """
        Updates scheme of given url to the one used in Gerrit base_url.
        """
        if self.base_scheme and not url.startswith("%s://" % self.base_scheme):
            url_split = urlparse.urlsplit(url)
            url = urlparse.urlunsplit(
                [
                    self.base_scheme,
                    url_split.netloc,
                    url_split.path,
                    url_split.query,
                    url_split.fragment
                ]
            )
        return url

    def get_request_dict(
        self, params=None, data=None, json=None, headers=None, **kwargs
    ):
        """
        :param params:
        :param data:
        :param json:
        :param headers:
        :param kwargs:
        :return:
        """
        request_kwargs = kwargs
        if self.username and self.password:
            request_kwargs["auth"] = (self.username, self.password)

        if params:
            assert isinstance(params, dict), f"Params must be a dict, got {repr(params)}"
            request_kwargs["params"] = params

        if headers:
            assert isinstance(headers, dict), f"headers must be a dict, got {repr(headers)}"
            request_kwargs["headers"] = headers

        if self.AUTH_COOKIE:
            currentheaders = request_kwargs.get("headers", {})
            currentheaders.update({"Cookie": self.AUTH_COOKIE})
            request_kwargs["headers"] = currentheaders

        request_kwargs["verify"] = self.ssl_verify
        request_kwargs["cert"] = self.cert

        if data and json:
            raise ValueError("Cannot use data and json together")

        if data:
            request_kwargs["data"] = data

        if json:
            request_kwargs["json"] = json

        request_kwargs["timeout"] = self.timeout

        return request_kwargs

    def get(
        self,
        url,
        params=None,
        headers=None,
        allow_redirects=True,
        stream=False,
        **kwargs
    ):
        """
        :param url:
        :param params:
        :param headers:
        :param allow_redirects:
        :param stream:
        :param kwargs:
        :return:
        """
        request_kwargs = self.get_request_dict(
            params=params,
            headers=headers,
            allow_redirects=allow_redirects,
            stream=stream,
            **kwargs
        )
        return self.confirm_status(self.session.get(self._update_url_scheme(url), **request_kwargs))

    def post(
        self,
        url,
        params=None,
        data=None,
        json=None,
        files=None,
        headers=None,
        allow_redirects=True,
        **kwargs
    ):
        """
        :param url:
        :param params:
        :param data:
        :param json:
        :param files:
        :param headers:
        :param allow_redirects:
        :param kwargs:
        :return:
        """
        request_kwargs = self.get_request_dict(
            params=params,
            data=data,
            json=json,
            files=files,
            headers=headers,
            allow_redirects=allow_redirects,
            **kwargs
        )
        return self.confirm_status(self.session.post(self._update_url_scheme(url), **request_kwargs))

    def put(
        self,
        url,
        params=None,
        data=None,
        json=None,
        files=None,
        headers=None,
        allow_redirects=True,
        **kwargs
    ):
        """
        :param url:
        :param params:
        :param data:
        :param json:
        :param files:
        :param headers:
        :param allow_redirects:
        :param kwargs:
        :return:
        """
        request_kwargs = self.get_request_dict(
            params=params,
            data=data,
            json=json,
            files=files,
            headers=headers,
            allow_redirects=allow_redirects,
            **kwargs
        )
        return self.confirm_status(self.session.put(self._update_url_scheme(url), **request_kwargs))

    def delete(self, url, headers=None, allow_redirects=True, **kwargs):
        """
        :param url:
        :param headers:
        :param allow_redirects:
        :param kwargs:
        :return:
        """
        request_kwargs = self.get_request_dict(
            headers=headers, allow_redirects=allow_redirects, **kwargs
        )
        return self.confirm_status(self.session.delete(self._update_url_scheme(url), **request_kwargs))

    @staticmethod
    def confirm_status(res):
        """
        check response status code
        :param res:
        :return:
        """
        http_error_msg = ""
        if isinstance(res.reason, bytes):
            # We attempt to decode utf-8 first because some servers
            # choose to localize their reason strings. If the string
            # isn't utf-8, we fall back to iso-8859-1 for all other
            # encodings. (See PR #3538)
            try:
                reason = res.reason.decode("utf-8")
            except UnicodeDecodeError:
                reason = res.reason.decode("iso-8859-1")
        else:
            reason = res.reason

        if 400 <= res.status_code < 500:
            http_error_msg = f"{res.status_code} Client Error: {reason} for url: {res.url}"

        elif 500 <= res.status_code < 600:
            http_error_msg = f"{res.status_code} Server Error: {reason} for url: {res.url}"

        if res.status_code < 300:
            # OK, return http response
            return res

        elif res.status_code == 400:
            # Validation error
            raise ValidationError(http_error_msg)

        elif res.status_code == 401:
            # Unauthorized error
            raise UnauthorizedError(http_error_msg)

        elif res.status_code == 403:
            # Auth error
            raise AuthError(http_error_msg)

        elif res.status_code == 404:
            # Not Found
            raise NotFoundError(http_error_msg)

        elif res.status_code == 405:
            # Method Not Allowed
            raise NotAllowedError(http_error_msg)

        elif res.status_code == 409:
            # Conflict
            raise ConflictError(http_error_msg)

        elif res.status_code < 500:
            # Other 4xx, generic client error
            raise ClientError(http_error_msg)

        else:
            # 5xx is server error
            raise ServerError(http_error_msg)
