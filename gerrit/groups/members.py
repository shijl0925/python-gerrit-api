#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi


class GerritGroupMembers(object):
    def __init__(self, group_id, gerrit):
        self.group_id = group_id
        self.gerrit = gerrit
        self.endpoint = f"/groups/{self.group_id}/members"

    def list(self):
        """
        Lists the direct members of a Gerrit internal group.
        This endpoint is only allowed for Gerrit internal groups;
        attempting to call on a non-internal group will return 405 Method Not Allowed.

        :return:
        """
        result = self.gerrit.get(self.endpoint)

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
        result = self.gerrit.get(self.endpoint + f"/{username}")
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
        result = self.gerrit.put(self.endpoint + f"/{username}")
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
        self.gerrit.delete(self.endpoint + f"/{username}")
