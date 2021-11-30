#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from gerrit.utils.models import BaseModel
from gerrit.groups.members import GerritGroupMembers
from gerrit.groups.subgroups import GerritGroupSubGroups


class GerritGroup(BaseModel):
    def __init__(self, **kwargs):
        super(GerritGroup, self).__init__(**kwargs)
        self.entity_name = "name"

    def get_name(self):
        """
        Retrieves the name of a group.

        :return:
        """
        endpoint = "/groups/%s/name" % self.id
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.get(base_url)
        result = self.gerrit.decode_response(response)

        return result

    def set_name(self, input_):
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
        endpoint = "/groups/%s/name" % self.id
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)

        return result

    def get_description(self):
        """
        Retrieves the description of a group.

        :return:
        """
        endpoint = "/groups/%s/description" % self.id
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.get(base_url)
        result = self.gerrit.decode_response(response)

        return result

    def set_description(self, input_):
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
        endpoint = "/groups/%s/description" % self.id
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)

        return result

    def delete_description(self):
        """
        Deletes the description of a Gerrit internal group.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        :return:
        """
        endpoint = "/groups/%s/description" % self.id
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))

    def get_options(self):
        """
        Retrieves the options of a group.

        :return:
        """
        endpoint = "/groups/%s/options" % self.id
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.get(base_url)
        result = self.gerrit.decode_response(response)
        return result

    def set_options(self, input_):
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
        endpoint = "/groups/%s/options" % self.id
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def get_owner(self):
        """
        Retrieves the owner group of a Gerrit internal group.

        :return: As response a GroupInfo entity is returned that describes the owner group.
        """
        endpoint = "/groups/%s/owner" % self.id
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.get(base_url)
        result = self.gerrit.decode_response(response)
        return result

    def set_owner(self, input_):
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

        :param input_: As response a GroupInfo entity is returned that describes the new owner group.
        :return:
        """
        endpoint = "/groups/%s/owner" % self.id
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)

        return result

    def get_audit_log(self):
        """
        Gets the audit log of a Gerrit internal group.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        :return:
        """
        endpoint = "/groups/%s/log.audit" % self.id
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def index(self):
        """
        Adds or updates the internal group in the secondary index.

        :return:
        """
        endpoint = "/groups/%s/index" % self.id
        self.gerrit.requester.post(self.gerrit.get_endpoint_url(endpoint))

    @property
    def members(self):
        return GerritGroupMembers(group_id=self.id, gerrit=self.gerrit)

    @property
    def subgroup(self):
        return GerritGroupSubGroups(group_id=self.id, gerrit=self.gerrit)
