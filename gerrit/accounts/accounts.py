#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from gerrit.accounts.account import GerritAccount


class GerritAccounts(object):
    def __init__(self, gerrit):
        self.gerrit = gerrit

    def search(
        self,
        query,
        limit=None,
        skip=None,
        detailed=False,
        suggested=False,
        all_emails=False,
    ):
        """
        Queries accounts visible to the caller.

        :param query: Query string
        :param limit: Int value that allows to limit the number of accounts
                      to be included in the output results
        :param skip: Int value that allows to skip the given
                     number of accounts from the beginning of the list
        :param detailed: boolean value, if True then full name,
                         preferred email, username and avatars for each account
                         will be added to the output result
        :param suggested: boolean value, if True get account suggestions
                          based on query string. If a result limit n is not
                          specified, then the default 10 is used.
        :param all_emails: boolean value, if True then all registered emails
                           for each account will be added to the output result
        :return:
        """
        option = filter(
            None,
            ["DETAILS" if detailed else None, "ALL_EMAILS" if all_emails else None],
        )
        option = None if not option else option
        params = {
            k: v for k, v in (("n", limit), ("S", skip), ("o", option)) if v is not None
        }

        endpoint = "/accounts/{suggest}{query}".format(
            suggest="?suggest&" if suggested else "?",
            query="q={query}".format(query=query),
        )

        response = self.gerrit.requester.get(
            self.gerrit.get_endpoint_url(endpoint), params
        )
        result = self.gerrit.decode_response(response)

        return result

    def get(self, username, detailed=False):
        """
        Returns an account

        :param username: username or _account_id
        :param detailed: boolean type, If True then fetch info in more details, such as: registered_on
        :return:
        """
        endpoint = "/accounts/{username}/{detail}".format(
            username=username, detail="detail" if detailed else ""
        )
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return GerritAccount.parse(result, gerrit=self.gerrit)

    def create(self, username, input_):
        """
        Creates a new account.

        .. code-block:: python

            input_ = {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "ssh_key": "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA0T...YImydZAw==",
                "http_password": "19D9aIn7zePb",
                "groups": [
                  "MyProject-Owners"
                ]
            }
            new_account = client.accounts.create('john.doe', input_)

        :param username: account username
        :param input_: the AccountInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-accounts.html#account-input
        :return:
        """
        endpoint = "/accounts/%s" % username
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return GerritAccount.parse(result, gerrit=self.gerrit)
