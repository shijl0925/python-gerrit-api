#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from gerrit.groups.group import GerritGroup
from gerrit.utils.common import params_creator
from packaging.version import parse


class GerritGroups(object):
    def __init__(self, gerrit):
        self.gerrit = gerrit
        self.endpoint = "/groups"

    def list(self, pattern_dispatcher=None, options=None, limit=None, skip=None):
        """
        Lists the groups accessible by the caller.

        :param pattern_dispatcher: Dict of pattern type with respective
                     pattern value: {('match'|'regex') : value}
        :param options: Additional fields can be obtained by adding o parameters,
                        each option requires more lookups and slows down the query response time to
                        the client so they are generally disabled by default. Optional fields are:
                          INCLUDES: include list of direct subgroups.
                          MEMBERS: include list of direct group members.
        :param limit: Int value that allows to limit the number of groups
                      to be included in the output results
        :param skip: Int value that allows to skip the given
                     number of groups from the beginning of the list
        :return:
        """
        params = params_creator((("o", options), ("n", limit), ("S", skip)),
                                {"match": "m", "regex": "r"}, pattern_dispatcher)

        return self.gerrit.get(self.endpoint, params=params)

    def search(self, query, options=None, limit=None, skip=None):
        """
        Query Groups

        :param query:
        :param options: Additional fields can be obtained by adding o parameters,
                        each option requires more lookups and slows down the query response time to
                        the client so they are generally disabled by default. Optional fields are:
                          INCLUDES: include list of direct subgroups.
                          MEMBERS: include list of direct group members.
        :param limit: Int value that allows to limit the number of groups
                      to be included in the output results
        :param skip: Int value that allows to skip the given
                     number of groups from the beginning of the list
        :return:
        """
        version = self.gerrit.version
        if parse(version) < parse("3.2.0"):
            endpoint = self.endpoint + f"/?query2={query}"
        else:
            endpoint = self.endpoint + f"/?query={query}"

        params = {
            k: v
            for k, v in (("o", options), ("limit", limit), ("start", skip))
            if v is not None
        }

        return self.gerrit.get(endpoint, params=params)

    def get(self, id_, detailed=False):
        """
        Retrieves a group.

        :param id_: group id, or group_id, or group name
        :param detailed:
        :return:
        """
        endpoint = self.endpoint + f"/{id_}/"
        if detailed:
            endpoint += "detail"
        return GerritGroup(json=self.gerrit.get(endpoint), gerrit=self.gerrit)

    def create(self, name, input_):
        """
        Creates a new Gerrit internal group.

        .. code-block:: python

            input_ = {
                "description": "contains all committers for MyProject2",
                "visible_to_all": 'true',
                "owner": "Administrators",
                "owner_id": "af01a8cb8cbd8ee7be072b98b1ee882867c0cf06"
            }
            new_group = client.groups.create('My-Project2-Committers', input_)

        :param name: group name
        :param input_: the GroupInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#group-input
        :return:
        """
        result = self.gerrit.put(
            self.endpoint + f"/{name}", json=input_, headers=self.gerrit.default_headers)
        return GerritGroup(json=result, gerrit=self.gerrit)
