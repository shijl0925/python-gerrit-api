#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi

from gerrit.utils.models import BaseModel


class GerrirProjectWebHook(BaseModel):
    def __init__(self, **kwargs):
        super(GerrirProjectWebHook, self).__init__(**kwargs)
        self.entity_name = "name"

    def delete(self):
        """
        Delete a webhook for a project.

        :return:
        """
        endpoint = "/config/server/webhooks~projects/%s/remotes/%s" % (
            self.project,
            self.name,
        )
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))


class GerrirProjectWebHooks(object):
    def __init__(self, project, gerrit):
        self.project = project
        self.gerrit = gerrit

    def list(self):
        """
        List existing webhooks for a project.

        :return:
        """
        endpoint = "/config/server/webhooks~projects/%s/remotes/" % self.project
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)

        webhooks = []
        for key, value in result.items():
            webhook = value
            webhook.update({"name": key})
            webhooks.append(webhook)

        return GerrirProjectWebHook.parse_list(
            webhooks, project=self.project, gerrit=self.gerrit
        )

    def create(self, name, input_):
        """
        Create or update a webhook for a project.

        .. code-block:: python

            input_ = {
                "url": "https://foo.org/gerrit-events",
                "maxTries": "3",
                "sslVerify": "true"
            }

            project = client.projects.get('myproject')
            new_webhook = project.webhooks.create('test', input_)

        :param name: the webhook name
        :param input_: the RemoteInfo entity
        :return:
        """
        endpoint = "/config/server/webhooks~projects/%s/remotes/%s" % (
            self.project,
            name,
        )
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return GerrirProjectWebHook.parse(
            result, project=self.project, gerrit=self.gerrit
        )

    def get(self, name):
        """
        Get information about one webhook.

        :param name: the webhook name
        :return:
        """
        endpoint = "/config/server/webhooks~projects/%s/remotes/%s" % (
            self.project,
            name,
        )
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        result.update({"name": name})
        return GerrirProjectWebHook.parse(
            result, project=self.project, gerrit=self.gerrit
        )

    def delete(self, name):
        """
        Delete a webhook for a project.

        :param name: the webhook name
        :return:
        """
        endpoint = "/config/server/webhooks~projects/%s/remotes/%s" % (
            self.project,
            name,
        )
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))
