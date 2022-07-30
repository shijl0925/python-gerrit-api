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
        self.gerrit.delete(f"/config/server/webhooks~projects/{self.project}/remotes/{self.name}")


class GerrirProjectWebHooks(object):
    def __init__(self, project, gerrit):
        self.project = project
        self.gerrit = gerrit

    def list(self):
        """
        List existing webhooks for a project.

        :return:
        """
        result = self.gerrit.get(f"/config/server/webhooks~projects/{self.project}/remotes/")

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
        endpoint = f"/config/server/webhooks~projects/{self.project}/remotes/{name}"
        result = self.gerrit.put(endpoint, json=input_, headers=self.gerrit.default_headers)
        return GerrirProjectWebHook.parse(result, project=self.project, gerrit=self.gerrit)

    def get(self, name):
        """
        Get information about one webhook.

        :param name: the webhook name
        :return:
        """
        endpoint = f"/config/server/webhooks~projects/{self.project}/remotes/{name}"
        result = self.gerrit.get(endpoint)
        result.update({"name": name})
        return GerrirProjectWebHook.parse(result, project=self.project, gerrit=self.gerrit)

    def delete(self, name):
        """
        Delete a webhook for a project.

        :param name: the webhook name
        :return:
        """
        self.gerrit.delete(f"/config/server/webhooks~projects/{self.project}/remotes/{name}")
