#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from typing import Any
from gerrit import GerritClient


class GerritGroupSubGroups:
    def __init__(self, group_id: str, gerrit: GerritClient) -> None:
        self.id = group_id
        self.gerrit = gerrit
        self.endpoint = f"/groups/{self.id}/groups"

    def list(self) -> Any:
        """
        Lists the direct subgroups of a group.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        :return:
        """
        result = self.gerrit.get(self.endpoint + "/")
        subgroups = []
        for item in result:
            group_id = item.get("id")
            subgroups.append(self.gerrit.groups.get(group_id))

        return subgroups

    def get(self, subgroup) -> Any:
        """
        Retrieves a subgroup.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        :param subgroup: subgroup id or name
        :return:
        """
        result = self.gerrit.get(self.endpoint + f"/{subgroup}")

        subgroup_id = result.get("id")
        return self.gerrit.groups.get(subgroup_id)

    def add(self, subgroup) -> Any:
        """
        Adds an internal or external group as subgroup to a Gerrit internal group.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        :param subgroup: subgroup id or name
        :return:
        """
        result = self.gerrit.put(self.endpoint + f"/{subgroup}")

        subgroup_id = result.get("id")
        return self.gerrit.groups.get(subgroup_id)

    def add_subgroups(self, input_) -> Any:
        """
        Adds multiple groups as subgroups to a Gerrit internal group in a single request.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        .. code-block:: python

            input_ = {
                "groups": ["MyGroup", "MyOtherGroup"]
            }
            group = client.groups.get('0017af503a22f7b3fa6ce2cd3b551734d90701b4')
            result = group.subgroup.add_subgroups(input_)

        :param input_: the GroupsInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#add-subgroups
        :return:
        """
        return self.gerrit.post(
            self.endpoint, json=input_, headers=self.gerrit.default_headers
        )

    def remove(self, subgroup) -> None:
        """
        Removes a subgroup from a Gerrit internal group.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        :param subgroup: subgroup id or name
        :return:
        """
        self.gerrit.delete(self.endpoint + f"/{subgroup}")

    def remove_subgroups(self, input_) -> None:
        """
        Removes multiple subgroups from a Gerrit internal group in a single request.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        .. code-block:: python

            input_ = {
                "groups": ["MyGroup", "MyOtherGroup"]
            }
            group = client.groups.get('0017af503a22f7b3fa6ce2cd3b551734d90701b4')
            group.subgroup.remove_subgroups(input_)

        :param input_: the GroupsInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#remove-subgroups
        :return:
        """
        self.gerrit.post(
            self.endpoint + ".delete",
            json=input_,
            headers=self.gerrit.default_headers,
        )
