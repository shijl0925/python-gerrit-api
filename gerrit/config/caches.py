#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from typing import Any
from gerrit import GerritClient


class Cache:
    def __init__(self, name: str, gerrit: GerritClient) -> None:
        self.name = name
        self.gerrit = gerrit
        self.endpoint = f"/config/server/caches/{self.name}"

    def flush(self) -> None:
        """
        Flushes a cache.

        :return:
        """
        self.gerrit.post(self.endpoint + "/flush")


class Caches:
    def __init__(self, gerrit: GerritClient) -> None:
        self.gerrit = gerrit
        self.endpoint = "/config/server/caches"

    def list(self) -> Any:
        """
        Lists the caches of the server. Caches defined by plugins are included.

        :return:
        """
        result = self.gerrit.get(self.endpoint)
        caches = []
        for key, value in result.items():
            cache = value
            cache.update({"name": key})
            caches.append(cache)

        return caches

    def get(self, name: str) -> Any:
        """
        Retrieves information about a cache.

        :param name: cache name
        :return:
        """
        result = self.gerrit.get(self.endpoint + f"/{name}")

        name = result.get("name")
        return Cache(name=name, gerrit=self.gerrit)

    def flush(self, name: str) -> None:
        """
        Flushes a cache.

        :param name: cache name
        :return:
        """
        self.gerrit.post(self.endpoint + f"/{name}/flush")

    def operation(self, input_: Any) -> None:
        """
        Cache Operations

        .. code-block:: python

            input_ = {
                "operation": "FLUSH_ALL"
            }
            gerrit.config.caches.operation(input_)

        :param input_: the CacheOperationInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-config.html#cache-operation-input
        :return:
        """
        self.gerrit.post(
            self.endpoint, json=input_, headers=self.gerrit.default_headers
        )
