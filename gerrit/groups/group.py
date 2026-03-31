#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from typing import Any, Dict, List
from gerrit import GerritClient
from gerrit.utils.gerritbase import GerritBase
from gerrit.groups.members import GerritGroupMembers
from gerrit.groups.subgroups import GerritGroupSubGroups


class GerritGroup(GerritBase):
    def __init__(self, group_id: str, gerrit: GerritClient) -> None:
        self.id = group_id
        self.gerrit = gerrit
        self.endpoint = f"/groups/{self.id}"
        super().__init__()

    def __str__(self) -> str:
        return self.id

    def get_name(self) -> Any:
        """
        Retrieves the name of a group.

        :return:
        """
        return self.gerrit.get(self.endpoint + "/name")

    def get_detail(self) -> Any:
        """
        Retrieves a group with the direct members and the directly included groups.

        :return:
        """
        return self.gerrit.get(self.endpoint + "/detail")

    def set_name(self, input_: Dict[str, Any]) -> Any:
        """
        Renames a Gerrit internal group.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        .. code-block:: python

            input_ = {
                "name": "My Project Committers"
            }

            group = client.groups.get('0017af503a22f7b3fa6ce2cd3b551734d90701b4')
            result = group.set_name(input_)

        :param input_:
        :return:
        """
        return self.gerrit.put(
            self.endpoint + "/name", json=input_, headers=self.gerrit.default_headers
        )

    def get_description(self) -> Any:
        """
        Retrieves the description of a group.

        :return:
        """
        return self.gerrit.get(self.endpoint + "/description")

    def set_description(self, input_: Dict[str, Any]) -> Any:
        """
        Sets the description of a Gerrit internal group.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        .. code-block:: python

            input_ = {
                "description": "The committers of MyProject."
            }
            group = client.groups.get('0017af503a22f7b3fa6ce2cd3b551734d90701b4')
            result = group.set_description(input_)

        :param input_:
        :return:
        """
        return self.gerrit.put(
            self.endpoint + "/description",
            json=input_,
            headers=self.gerrit.default_headers,
        )

    def delete_description(self) -> None:
        """
        Deletes the description of a Gerrit internal group.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        :return:
        """
        self.gerrit.delete(self.endpoint + "/description")

    def get_options(self) -> Any:
        """
        Retrieves the options of a group.

        :return:
        """
        return self.gerrit.get(self.endpoint + "/options")

    def set_options(self, input_: Dict[str, Any]) -> Any:
        """
        Sets the options of a Gerrit internal group.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        .. code-block:: python

            input_ = {
                "visible_to_all": True
            }
            group = client.groups.get('0017af503a22f7b3fa6ce2cd3b551734d90701b4')
            result = group.set_options(input_)


        :param input_: the GroupOptionsInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#group-options-input
        :return:
        """
        return self.gerrit.put(
            self.endpoint + "/options", json=input_, headers=self.gerrit.default_headers
        )

    def get_owner(self) -> Any:
        """
        Retrieves the owner group of a Gerrit internal group.

        :return: As response a GroupInfo entity is returned that describes the owner group.
        """
        return self.gerrit.get(self.endpoint + "/owner")

    def set_owner(self, input_: Dict[str, Any]) -> Any:
        """
        Sets the owner group of a Gerrit internal group.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        .. code-block:: python

            input_ = {
                "owner": "6a1e70e1a88782771a91808c8af9bbb7a9871389"
            }
            group = client.groups.get('0017af503a22f7b3fa6ce2cd3b551734d90701b4')
            result = group.set_owner(input_)

        :param input_: As response a GroupInfo entity is returned that describes the new owner
        group.
        :return:
        """
        return self.gerrit.put(
            self.endpoint + "/owner", json=input_, headers=self.gerrit.default_headers
        )

    def get_audit_log(self) -> Any:
        """
        Gets the audit log of a Gerrit internal group.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        :return:
        """
        return self.gerrit.get(self.endpoint + "/log.audit")

    def index(self) -> None:
        """
        Adds or updates the internal group in the secondary index.

        :return:
        """
        self.gerrit.post(self.endpoint + "/index")

    @property
    def members(self) -> GerritGroupMembers:
        return GerritGroupMembers(group_id=self.id, gerrit=self.gerrit)

    @property
    def subgroup(self) -> GerritGroupSubGroups:
        return GerritGroupSubGroups(group_id=self.id, gerrit=self.gerrit)
