#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from gerrit.utils.models import BaseModel


class GerritAccountEmail(BaseModel):
    def __init__(self, **kwargs):
        super(GerritAccountEmail, self).__init__(**kwargs)
        self.entity_name = "email"

    def delete(self):
        """
        Deletes an email address of an account.

        :return:
        """
        self.gerrit.delete(f"/accounts/{self.username}/emails/{self.email}")

    def set_preferred(self):
        """
        Sets an email address as preferred email address for an account.

        :return:
        """
        self.gerrit.put(f"/accounts/{self.username}/emails/{self.email}/preferred")


class GerritAccountEmails(object):
    def __init__(self, username, gerrit):
        self.username = username
        self.gerrit = gerrit

    def list(self):
        """
        Returns the email addresses that are configured for the specified user.

        :return:
        """
        result = self.gerrit.get(f"/accounts/{self.username}/emails")
        return GerritAccountEmail.parse_list(result, username=self.username, gerrit=self.gerrit)

    def create(self, email):
        """
        Registers a new email address for the user.

        :return:
        """
        return self.gerrit.put(f"/accounts/{self.username}/emails/{email}")

    def get(self, email):
        """
        Retrieves an email address of a user.

        :return:
        """
        result = self.gerrit.get(f"/accounts/{self.username}/emails/{email}")
        return GerritAccountEmail(json=result, username=self.username, gerrit=self.gerrit)

    def set_preferred(self, email):
        """
        Sets an email address as preferred email address for an account.

        :param email: account email
        :return:
        """
        self.gerrit.put(f"/accounts/{self.username}/emails/{email}/preferred")

    def delete(self, email):
        """
        Deletes an email address of an account.

        :param email: account email
        :return:
        """
        self.gerrit.delete(f"/accounts/{self.username}/emails/{email}")
