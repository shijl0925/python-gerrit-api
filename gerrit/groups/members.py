#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi


class GerritGroupMembers(object):
    def __init__(self, group_id, gerrit):
        self.group_id = group_id
        self.gerrit = gerrit

    def list(self):
        """
        Lists the direct members of a Gerrit internal group.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        :return:
        """
        endpoint = "/groups/%s/members/" % self.group_id
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)

        accounts = []
        for item in result:
            username = item.get("username")
            accounts.append(self.gerrit.accounts.get(username))

        return accounts

    def get(self, username):
        """
        Retrieves a group member.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        :param username: account username
        :return:
        """
        endpoint = "/groups/%s/members/%s" % (self.group_id, username)
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        if result:
            username = result.get("username")
            return self.gerrit.accounts.get(username)

    def add(self, username):
        """
        Adds a user as member to a Gerrit internal group.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        :param username: account username
        :return:
        """
        endpoint = "/groups/%s/members/%s" % (self.group_id, username)
        response = self.gerrit.requester.put(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        if result:
            username = result.get("username")
            return self.gerrit.accounts.get(username)

    def remove(self, username):
        """
        Removes a user from a Gerrit internal group.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        :param username: account username
        :return:
        """
        endpoint = "/groups/%s/members/%s" % (self.group_id, username)
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))