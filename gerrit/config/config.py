#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from gerrit.config.caches import Caches
from gerrit.config.tasks import Tasks


class GerritConfig(object):
    def __init__(self, gerrit):
        self.gerrit = gerrit

    def get_version(self):
        """
        get the version of the Gerrit server.

        :return:
        """
        endpoint = "/config/server/version"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def get_server_info(self):
        """
        get the information about the Gerrit server configuration.

        :return:
        """
        endpoint = "/config/server/info"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def check_consistency(self, input_):
        """
        Runs consistency checks and returns detected problems.

        .. code-block:: python

            input_ = {
                "check_accounts": {},
                "check_account_external_ids": {}
            }
            result = client.config.check_consistency(input_)

        :param input_: the ConsistencyCheckInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-config.html#consistency-check-input
        :return:
        """
        endpoint = "/config/server/check.consistency"
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.post(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def reload_config(self):
        """
        Reloads the gerrit.config configuration.

        :return:
        """
        endpoint = "/config/server/reload"
        response = self.gerrit.requester.post(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def confirm_email(self, input_):
        """
        Confirms that the user owns an email address.
        If the token is invalid or if it's the token of another user the request fails and the response is
        '422 Unprocessable Entity'.

        .. code-block:: python

            input_ = {
                "token": "Enim+QNbAo6TV8Hur8WwoUypI6apG7qBPvF+bw==$MTAwMDAwNDp0ZXN0QHRlc3QuZGU="
            }
            result = client.config.confirm_email(input_)

        :param input_: the EmailConfirmationInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-config.html#email-confirmation-input
        :return:
        """
        endpoint = "/config/server/email.confirm"
        base_url = self.gerrit.get_endpoint_url(endpoint)
        self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )

    @property
    def caches(self):
        return Caches(gerrit=self.gerrit)

    def get_summary(self, option=None):
        """
        Retrieves a summary of the current server state.

        :param option: query option.such as jvm or gc
        :return:
        """
        endpoint = "/config/server/summary"
        if option is not None:
            endpoint += "?%s" % option
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def list_capabilities(self):
        """
        Lists the capabilities that are available in the system.
        There are two kinds of capabilities: core and plugin-owned capabilities.

        :return:
        """
        endpoint = "/config/server/capabilities"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    @property
    def tasks(self):
        return Tasks(gerrit=self.gerrit)

    def get_top_menus(self):
        """
        Returns the list of additional top menu entries.

        :return:
        """
        endpoint = "/config/server/top-menus"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def get_default_user_preferences(self):
        """
        Returns the default user preferences for the server.

        :return:
        """
        endpoint = "/config/server/preferences"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def set_default_user_preferences(self, input_):
        """
        Sets the default user preferences for the server.

        .. code-block:: python

            input_ = {
                "changes_per_page": 50
            }
            result = client.config.set_default_user_preferences(input_)

        :param input_: the PreferencesInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-accounts.html#preferences-input
        :return:
        """
        endpoint = "/config/server/preferences"
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def get_default_diff_preferences(self):
        """
        Returns the default diff preferences for the server.

        :return:
        """
        endpoint = "/config/server/preferences.diff"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def set_default_diff_preferences(self, input_):
        """
        Sets the default diff preferences for the server.

        .. code-block:: python

            input_ = {
                "context": 10,
                "tab_size": 8,
                "line_length": 80,
                "cursor_blink_rate": 0,
                "intraline_difference": true,
                "show_line_endings": true,
                "show_tabs": true,
                "show_whitespace_errors": true,
                "syntax_highlighting": true,
                "auto_hide_diff_table_header": true,
                "theme": "DEFAULT",
                "ignore_whitespace": "IGNORE_NONE"
            }
            result = client.config.set_default_diff_preferences(input_)

        :param input_: the DiffPreferencesInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-accounts.html#diff-preferences-input
        :return:
        """
        endpoint = "/config/server/preferences.diff"
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def get_default_edit_preferences(self):
        """
        Returns the default edit preferences for the server.

        :return:
        """
        endpoint = "/config/server/preferences.edit"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def set_default_edit_preferences(self, input_):
        """
        Sets the default edit preferences for the server.

        .. code-block:: python

            input_ = {
                "tab_size": 8,
                "line_length": 80,
                "indent_unit": 2,
                "cursor_blink_rate": 0,
                "show_tabs": true,
                "syntax_highlighting": true,
                "match_brackets": true,
                "auto_close_brackets": true,
                "theme": "DEFAULT",
                "key_map_type": "DEFAULT"
            }
            result = client.config.set_default_edit_preferences(input_)

        :param input_: the EditPreferencesInfo entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-accounts.html#edit-preferences-input
        :return:
        """
        endpoint = "/config/server/preferences.edit"
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def index_changes(self, input_):
        """
        Index a set of changes

        .. code-block:: python

            input_ = {changes: ["foo~101", "bar~202"]}
            gerrit.config.index_changes(input_)

        :param input_: the IndexChangesInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-config.html#index-changes-input
        :return:
        """
        endpoint = "/config/server/index.changes"
        base_url = self.gerrit.get_endpoint_url(endpoint)
        self.gerrit.requester.post(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
