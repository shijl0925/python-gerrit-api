#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from gerrit.changes.change import GerritChange


class GerritChanges(object):
    def __init__(self, gerrit):
        self.gerrit = gerrit

    def search(self, query, options=None, limit=None, skip=None):
        """
        Queries changes visible to the caller.

        .. code-block:: python

            query = ["is:open+owner:self", "is:open+reviewer:self+-owner:self", "is:closed+owner:self+limit:5"]
            result = client.changes.search(query=query, options=["LABELS"])

        :param query: Queries as a list of string
        :param options: List of options to fetch additional data about changes
        :param limit: Int value that allows to limit the number of changes
                      to be included in the output results
        :param skip: Int value that allows to skip the given number of
                     changes from the beginning of the list
        :return:
        """
        params = {
            k: v
            for k, v in (("o", options), ("n", limit), ("S", skip))
            if v is not None
        }

        endpoint = "/changes/{query}".format(
            query="?q={query}".format(query="&q=".join(query))
        )

        response = self.gerrit.requester.get(
            self.gerrit.get_endpoint_url(endpoint), params
        )
        result = self.gerrit.decode_response(response)
        return result

    def get(self, id_, detailed=False, options=None):
        """
        Retrieves a change.

        :param id_: change id
        :param detailed: boolean value, if True then retrieve a change with
                         labels, detailed labels, detailed accounts,
                         reviewer updates, and messages.
        :param options: List of options to fetch additional data about a change
        :return:
        """
        endpoint = "/changes/{id_}/{detail}".format(
            id_=id_, detail="detail" if detailed else ""
        )
        params = {"o": options}

        response = self.gerrit.requester.get(
            self.gerrit.get_endpoint_url(endpoint), params
        )
        result = self.gerrit.decode_response(response)
        return GerritChange.parse(result, gerrit=self.gerrit)

    def create(self, input_):
        """
        create a change

        .. code-block:: python

            input_ = {
                "project": "myProject",
                "subject": "Let's support 100% Gerrit workflow direct in browser",
                "branch": "stable",
                "topic": "create-change-in-browser",
                "status": "NEW"
            }
            result = client.changes.create(input_)

        :param input_: the ChangeInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#change-input
        :return:
        """
        endpoint = "/changes/"
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.post(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return GerritChange.parse(result, gerrit=self.gerrit)

    def delete(self, id_):
        """
        Deletes a change.

        :param id_: change id
        :return:
        """
        endpoint = "/changes/%s" % id_
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))
