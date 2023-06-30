#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import six.moves.urllib.parse as urlparse
from requests import Session
from requests.adapters import HTTPAdapter


class Requester:

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
        if self.base_scheme and not url.startswith(f"{self.base_scheme}://"):
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
        raise_for_status: bool = True,
        **kwargs
    ):
        """
        :param url:
        :param params:
        :param headers:
        :param allow_redirects:
        :param stream:
        :param raise_for_status:
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
        response = self.session.get(self._update_url_scheme(url), **request_kwargs)
        if raise_for_status:
            response.raise_for_status()
        return response

    def post(
        self,
        url,
        params=None,
        data=None,
        json=None,
        files=None,
        headers=None,
        allow_redirects=True,
        raise_for_status: bool = True,
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
        :param raise_for_status:
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
        response = self.session.post(self._update_url_scheme(url), **request_kwargs)
        if raise_for_status:
            response.raise_for_status()
        return response

    def put(
        self,
        url,
        params=None,
        data=None,
        json=None,
        files=None,
        headers=None,
        allow_redirects=True,
        raise_for_status: bool = True,
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
        :param raise_for_status:
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
        response = self.session.put(self._update_url_scheme(url), **request_kwargs)
        if raise_for_status:
            response.raise_for_status()
        return response

    def delete(self, url, headers=None, allow_redirects=True, raise_for_status: bool = True, **kwargs):
        """
        :param url:
        :param headers:
        :param allow_redirects:
        :param raise_for_status:
        :param kwargs:
        :return:
        """
        request_kwargs = self.get_request_dict(
            headers=headers, allow_redirects=allow_redirects, **kwargs
        )
        response = self.session.delete(self._update_url_scheme(url), **request_kwargs)
        if raise_for_status:
            response.raise_for_status()
        return response
