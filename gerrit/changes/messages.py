#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi

from gerrit.utils.models import BaseModel


class GerritChangeMessage(BaseModel):
    def __init__(self, **kwargs):
        super(GerritChangeMessage, self).__init__(**kwargs)

    def delete(self, input_=None):
        """
        Deletes a change message.
        Note that only users with the Administrate Server global capability are permitted to delete a change message.

        .. code-block:: python

            input_ = {
                "reason": "spam"
            }
            change = client.changes.get('myProject~stable~I10394472cbd17dd12454f229e4f6de00b143a444')
            message = change.messages.get("babf4c5dd53d7a11080696efa78830d0a07762e6")
            result = message.delete(input_)
            # or
            result = message.delete()

        :param input_: the DeleteChangeMessageInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#delete-change-message-input
        :return:
        """
        endpoint = f"/changes/{self.change}/messages/{self.id}"
        if input_ is None:
            self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))
        else:
            endpoint += "/delete"
            base_url = self.gerrit.get_endpoint_url(endpoint)
            response = self.gerrit.requester.post(
                base_url, json=input_, headers=self.gerrit.default_headers
            )
            result = self.gerrit.decode_response(response)
            change = self.gerrit.changes.get(self.change)
            return change.messages.get(result.get("id"))


class GerritChangeMessages(object):
    def __init__(self, change, gerrit):
        self.change = change
        self.gerrit = gerrit

    def list(self):
        """
        Lists all the messages of a change including detailed account information.

        :return:
        """
        endpoint = f"/changes/{self.change}/messages"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return GerritChangeMessage.parse_list(
            result, change=self.change, gerrit=self.gerrit
        )

    def get(self, id_):
        """
        Retrieves a change message including detailed account information.

        :param id_: change message id
        :return:
        """
        endpoint = f"/changes/{self.change}/messages/{id_}"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return GerritChangeMessage.parse(result, change=self.change, gerrit=self.gerrit)
