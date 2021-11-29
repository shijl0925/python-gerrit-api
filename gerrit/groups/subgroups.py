#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi


class GerritGroupSubGroups(object):
    def __init__(self, group_id, gerrit):
        self.group_id = group_id
        self.gerrit = gerrit

    def list(self):
        """
        Lists the direct subgroups of a group.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        :return:
        """
        endpoint = "/groups/%s/groups/" % self.group_id
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        subgroups = []
        for item in result:
            group_id = item.get("id")
            subgroups.append(self.gerrit.groups.get(group_id))

        return subgroups

    def get(self, subgroup):
        """
        Retrieves a subgroup.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        :param subgroup: subgroup id or name
        :return:
        """
        endpoint = "/groups/%s/groups/%s" % (self.group_id, subgroup)
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        if result:
            subgroup_id = result.get("id")
            return self.gerrit.groups.get(subgroup_id)

    def add(self, subgroup):
        """
        Adds an internal or external group as subgroup to a Gerrit internal group.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        :param subgroup: subgroup id or name
        :return:
        """
        endpoint = "/groups/%s/groups/%s" % (self.group_id, subgroup)
        response = self.gerrit.requester.put(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        if result:
            subgroup_id = result.get("id")
            return self.gerrit.groups.get(subgroup_id)

    def remove(self, subgroup):
        """
        Removes a subgroup from a Gerrit internal group.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        :param subgroup: subgroup id or name
        :return:
        """
        endpoint = "/groups/%s/groups/%s" % (self.group_id, subgroup)
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))