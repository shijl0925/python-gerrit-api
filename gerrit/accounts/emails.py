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
        endpoint = "/accounts/%s/emails/%s" % (self.username, self.email)
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))

    def set_preferred(self):
        """
        Sets an email address as preferred email address for an account.

        :return:
        """
        endpoint = "/accounts/%s/emails/%s/preferred" % (self.username, self.email)
        self.gerrit.requester.put(self.gerrit.get_endpoint_url(endpoint))


class GerritAccountEmails(object):
    def __init__(self, username, gerrit):
        self.username = username
        self.gerrit = gerrit

    def list(self):
        """
        Returns the email addresses that are configured for the specified user.

        :return:
        """
        endpoint = "/accounts/%s/emails" % self.username
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return GerritAccountEmail.parse_list(
            result, username=self.username, gerrit=self.gerrit
        )

    def create(self, email):
        """
        Registers a new email address for the user.

        :return:
        """
        endpoint = "/accounts/%s/emails/%s" % (self.username, email)
        response = self.gerrit.requester.put(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def get(self, email):
        """
        Retrieves an email address of a user.

        :return:
        """
        endpoint = "/accounts/%s/emails/%s" % (self.username, email)
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return GerritAccountEmail.parse(
            result, username=self.username, gerrit=self.gerrit
        )

    def set_preferred(self, email):
        """
        Sets an email address as preferred email address for an account.

        :param email: account email
        :return:
        """
        endpoint = "/accounts/%s/emails/%s/preferred" % (self.username, email)
        self.gerrit.requester.put(self.gerrit.get_endpoint_url(endpoint))

    def delete(self, email):
        """
        Deletes an email address of an account.

        :param email: account email
        :return:
        """
        endpoint = "/accounts/%s/emails/%s" % (self.username, email)
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))
