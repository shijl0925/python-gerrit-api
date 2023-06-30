#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from typing import Optional
from base64 import b64decode
from gerrit.utils.requester import Requester
from gerrit.utils.common import (
    decode_response,
    strip_trailing_slash
)


class GitilesClient:
    def __init__(
        self,
        base_url,
        username=None,
        password=None,
        ssl_verify=True,
        cert=None,
        timeout=60,
        max_retries=None,
    ):
        self._base_url = strip_trailing_slash(base_url)

        self.requester = Requester(
            base_url=base_url,
            username=username,
            password=password,
            ssl_verify=ssl_verify,
            cert=cert,
            timeout=timeout,
            max_retries=max_retries,
        )

    def get_endpoint_url(self, endpoint):
        """
        Return the complete url including host and port for a given endpoint.
        :param endpoint: service endpoint as str
        :return: complete url (including host and port) as str
        """
        return f"{self._base_url}{endpoint}"

    def commit(self, repo: str, commit: str):
        """Retrieves a commit."""
        endpoint = f"/{repo}/+/{commit}"
        params = {"format": "JSON"}

        response = self.requester.get(self.get_endpoint_url(endpoint), params=params)
        result = decode_response(response)

        return result

    def commits(self, repo: str, ref: str, start: Optional[str] = None):
        """query commit history"""
        endpoint = f"/{repo}/+log/{ref}"
        params = {"format": "JSON"}
        if start is not None:
            params.update({"s": start})

        response = self.requester.get(self.get_endpoint_url(endpoint), params=params)
        result = decode_response(response)

        return result

    def download_file(self, repo: str, ref: str, path: str, decode: bool = False):
        """Downloads raw file content from a Gitiles repository."""
        endpoint = f"/{repo}/+/{ref}/{path}"
        params = {"format": "TEXT"}

        response = self.requester.get(self.get_endpoint_url(endpoint), params=params)
        result = decode_response(response)

        if decode:
            return b64decode(result).decode("utf-8")

        return result
