#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from gerrit.utils.models import BaseModel


class Cache(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entity_name = "name"
        self.endpoint = "/config/server/caches"

    def flush(self):
        """
        Flushes a cache.

        :return:
        """
        self.gerrit.post(self.endpoint + f"/{self.name}/flush")


class Caches(object):
    def __init__(self, gerrit):
        self.gerrit = gerrit
        self.endpoint = "/config/server/caches"

    def list(self):
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

        return Cache.parse_list(caches, gerrit=self.gerrit)

    def get(self, name):
        """
        Retrieves information about a cache.

        :param name: cache name
        :return:
        """
        result = self.gerrit.get(self.endpoint + f"/{name}")
        return Cache(json=result, gerrit=self.gerrit)

    def flush(self, name):
        """
        Flushes a cache.

        :param name: cache name
        :return:
        """
        self.gerrit.post(self.endpoint + f"/{name}/flush")

    def operation(self, input_):
        """
        Cache Operations

        .. code-block:: python

            input_ = {
                "operation": "FLUSH_ALL"
            }
            gerrit.config.caches.operation(input_)

        :param input_: the CacheOperationInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-config.html
          #cache-operation-input
        :return:
        """
        self.gerrit.post(self.endpoint, json=input_, headers=self.gerrit.default_headers)
