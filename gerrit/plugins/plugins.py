#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from gerrit.utils.models import BaseModel


class GerritPlugin(BaseModel):
    def __init__(self, **kwargs):
        super(GerritPlugin, self).__init__(**kwargs)

    def enable(self):
        """
        Enables a plugin on the Gerrit server.

        :return:
        """
        result = self.gerrit.post(f"/plugins/{self.id}/gerrit~enable")
        return self.gerrit.plugins.get(result.get("id"))

    def disable(self):
        """
        Disables a plugin on the Gerrit server.

        :return:
        """
        result = self.gerrit.post(f"/plugins/{self.id}/gerrit~disable")
        return self.gerrit.plugins.get(result.get("id"))

    def reload(self):
        """
        Reloads a plugin on the Gerrit server.

        :return:
        """
        result = self.gerrit.post(f"/plugins/{self.id}/gerrit~reload")
        return self.gerrit.plugins.get(result.get("id"))


class GerritPlugins(object):
    def __init__(self, gerrit):
        self.gerrit = gerrit

    def list(self, is_all=False, limit=None, skip=None, pattern_dispatcher=None):
        """
        Lists the plugins installed on the Gerrit server.

        :param is_all: boolean value, if True then all plugins (including
                       hidden ones) will be added to the results
        :param limit: Int value that allows to limit the number of plugins
                      to be included in the output results
        :param skip: Int value that allows to skip the given
                     number of plugins from the beginning of the list
        :param pattern_dispatcher: Dict of pattern type with respective
                     pattern value: {('prefix'|'match'|'regex') : value}
        :return:
        """
        pattern_types = {"prefix": "p", "match": "m", "regex": "r"}

        p, v = None, None
        if pattern_dispatcher is not None and pattern_dispatcher:
            for item in pattern_types:
                if item in pattern_dispatcher:
                    p, v = pattern_types[item], pattern_dispatcher[item]
                    break
            else:
                raise ValueError(
                    "Pattern types can be either 'prefix', 'match' or 'regex'."
                )

        params = {k: v for k, v in (("n", limit), ("S", skip), (p, v)) if v is not None}
        params["all"] = int(is_all)

        return self.gerrit.get("/plugins/", params=params)

    def get(self, id_):
        """

        :param id_: plugin id
        :return:
        """
        result = self.gerrit.get(f"/plugins/{id_}/gerrit~status")
        return GerritPlugin.parse(result, gerrit=self.gerrit)

    def install(self, id_, input_):
        """
        Installs a new plugin on the Gerrit server.

        .. code-block:: python

            input_ = {
                "url": "file:///gerrit/plugins/delete-project/delete-project-2.8.jar"
            }

            plugin = client.plugins.install(input_)

        :param id_: plugin id
        :param input_: the PluginInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-plugins.html#plugin-input
        :return:
        """
        result = self.gerrit.put(
            f"/plugins/{id_}.jar", json=input_, headers=self.gerrit.default_headers
        )
        return GerritPlugin.parse(result, gerrit=self.gerrit)
