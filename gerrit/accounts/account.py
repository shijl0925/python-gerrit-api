#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from packaging.version import parse
from gerrit.utils.models import BaseModel
from gerrit.accounts.emails import GerritAccountEmails
from gerrit.accounts.ssh_keys import GerritAccountSSHKeys
from gerrit.accounts.gpg_keys import GerritAccountGPGKeys
from gerrit.utils.exceptions import UnsupportMethod


class GerritAccount(BaseModel):
    def __init__(self, **kwargs):
        super(GerritAccount, self).__init__(**kwargs)
        self.entity_name = "username"

    def get_name(self):
        """
        Retrieves the full name of an account.

        :return:
        """
        endpoint = f"/accounts/{self.username}/name"
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.get(base_url)
        result = self.gerrit.decode_response(response)
        return result

    def set_name(self, input_):
        """
        Sets the full name of an account.
        Some realms may not allow to modify the account name.
        In this case the request is rejected with '405 Method Not Allowed'.

        .. code-block:: python

            input_ = {
                "name": "Keven Shi"
            }

            account = client.accounts.get('kevin.shi')
            result = account.set_name(input_)


        :param input_: the AccountNameInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-accounts.html#account-name-input
        :return:
        """
        endpoint = f"/accounts/{self.username}/name"
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)

        return result

    def delete_name(self):
        """
        Deletes the name of an account.
        Some realms may not allow to delete the account name.
        In this case the request is rejected with '405 Method Not Allowed'.

        :return:
        """
        endpoint = f"/accounts/{self.username}/name"
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))

    def get_status(self):
        """
        Retrieves the status of an account.
        If the account does not have a status an empty string is returned.

        :getter: Retrieves the status of an account.
        :setter: Sets the status of an account

        :return:
        """
        endpoint = f"/accounts/{self.username}/status"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def set_status(self, status):
        """
        Sets the status of an account.

        :param status: account status
        :return:
        """
        endpoint = f"/accounts/{self.username}/status"
        input_ = {"status": status}
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def set_username(self, input_):
        """
        Sets the username of an account.
        Some realms may not allow to modify the account username.
        In this case the request is rejected with '405 Method Not Allowed'.

        .. code-block:: python

            input_ = {
                "username": "shijl0925.shi"
            }

            account = client.accounts.get('kevin.shi')
            result = account.set_username(input_)

        :param input_: the UsernameInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-accounts.html#username-input
        :return:
        """
        endpoint = f"/accounts/{self.username}/username"
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)

        return result

    def set_displayname(self, input_):
        """
        Sets the display name of an account.
        support this method since v3.2.0

        .. code-block:: python

            input_ = {
                "display_name": "Kevin"
            }

            account = client.accounts.get('kevin.shi')
            result = account.set_displayname(input_)

        :param input_: the DisplayNameInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-accounts.html#display-name-input
        :return:
        """
        version = self.gerrit.version
        if parse(version) < parse("3.2.0"):
            raise UnsupportMethod("The server does not support this method")

        endpoint = f"/accounts/{self.username}/displayname"
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)

        return result

    def get_active(self):
        """
        Checks if an account is active.

        :return:
        """
        endpoint = f"/accounts/{self.username}/active"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def set_active(self):
        """
        Sets the account state to active.

        :return:
        """
        endpoint = f"/accounts/{self.username}/active"
        self.gerrit.requester.put(self.gerrit.get_endpoint_url(endpoint))

    def delete_active(self):
        """
        Sets the account state to inactive.
        If the account was already inactive the response is '409 Conflict'.

        :return:
        """
        endpoint = f"/accounts/{self.username}/active"
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))

    def set_http_password(self, input_):
        """
        Sets/Generates the HTTP password of an account.

        .. code-block:: python

            input_ = {
                "generate": 'true',
                "http_password": "the_password"
            }

            account = client.accounts.get('kevin.shi')
            result = account.set_http_password(input_)

        :param input_: the HttpPasswordInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-accounts.html#http-password-input
        :return:
        """
        endpoint = f"/accounts/{self.username}/password.http"
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def delete_http_password(self):
        """
        Deletes the HTTP password of an account.

        :return:
        """
        endpoint = f"/accounts/{self.username}/password.http"
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))

    def get_oauth_token(self):
        """
        Returns a previously obtained OAuth access token.
        If there is no token available, or the token has already expired, '404 Not Found' is returned as response.
        Requests to obtain an access token of another user are rejected with '403 Forbidden'.

        :return:
        """
        endpoint = f"/accounts/{self.username}/oauthtoken"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    @property
    def emails(self):
        return GerritAccountEmails(username=self.username, gerrit=self.gerrit)

    @property
    def ssh_keys(self):
        return GerritAccountSSHKeys(username=self.username, gerrit=self.gerrit)

    @property
    def gpg_keys(self):
        return GerritAccountGPGKeys(username=self.username, gerrit=self.gerrit)

    def list_capabilities(self):
        """
        Returns the global capabilities that are enabled for the specified user.

        :return:
        """
        endpoint = f"/accounts/{self.username}/capabilities"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def check_capability(self, capability):
        """
        Checks if a user has a certain global capability.

        :param capability:
        :return:
        """
        endpoint = f"/accounts/{self.username}/capabilities/{capability}"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    @property
    def groups(self):
        """
        Lists all groups that contain the specified user as a member.

        :return:
        """
        endpoint = f"/accounts/{self.username}/groups"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return [self.gerrit.groups.get(item.get("id")) for item in result]

    def get_avatar(self):
        """
        Retrieves the avatar image of the user, requires avatars-gravatar plugin.

        :return:
        """
        endpoint = f"/accounts/{self.username}/avatar"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def get_avatar_change_url(self):
        """
        Retrieves the avatar image of the user, requires avatars-gravatar plugin.

        :return:
        """
        endpoint = f"/accounts/{self.username}/avatar.change.url"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def get_user_preferences(self):
        """
        Retrieves the user’s preferences.

        :return:
        """
        endpoint = f"/accounts/{self.username}/preferences"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def set_user_preferences(self, input_):
        """
        Sets the user’s preferences.

        .. code-block:: python

            input_ = {
                "changes_per_page": 50,
                "show_site_header": true,
                "use_flash_clipboard": true,
                "expand_inline_diffs": true,
                "download_command": "CHECKOUT",
                "date_format": "STD",
                "time_format": "HHMM_12",
                "size_bar_in_change_table": true,
                "review_category_strategy": "NAME",
                "diff_view": "SIDE_BY_SIDE",
                "mute_common_path_prefixes": true,
            }

            account = client.accounts.get('kevin.shi')
            result = account.set_user_preferences(input_)

        :param input_: the PreferencesInput entity，
          https://gerrit-review.googlesource.com/Documentation/rest-api-accounts.html#preferences-input
        :return:
        """
        endpoint = f"/accounts/{self.username}/preferences"
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def get_diff_preferences(self):
        """
        Retrieves the diff preferences of a user.

        :return:
        """
        endpoint = f"/accounts/{self.username}/preferences.diff"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def set_diff_preferences(self, input_):
        """
        Sets the diff preferences of a user.

        .. code-block:: python

            input_ = {
                "context": 10,
                "theme": "ECLIPSE",
                "ignore_whitespace": "IGNORE_ALL",
                "intraline_difference": true,
                "line_length": 100,
                "cursor_blink_rate": 500,
                "show_line_endings": true,
                "show_tabs": true,
                "show_whitespace_errors": true,
                "syntax_highlighting": true,
                "tab_size": 8,
                "font_size": 12
            }

            account = client.accounts.get('kevin.shi')
            result = account.set_diff_preferences(input_)

        :param input_: the DiffPreferencesInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-accounts.html#diff-preferences-input
        :return:
        """
        endpoint = f"/accounts/{self.username}/preferences.diff"
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def get_edit_preferences(self):
        """
        Retrieves the edit preferences of a user.

        :return:
        """
        endpoint = f"/accounts/{self.username}/preferences.edit"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def set_edit_preferences(self, input_):
        """
        Sets the edit preferences of a user.

        .. code-block:: python

            input_ = {
                "theme": "ECLIPSE",
                "key_map_type": "VIM",
                "tab_size": 4,
                "line_length": 80,
                "indent_unit": 2,
                "cursor_blink_rate": 530,
                "hide_top_menu": true,
                "show_tabs": true,
                "show_whitespace_errors": true,
                "syntax_highlighting": true,
                "hide_line_numbers": true,
                "match_brackets": true,
                "line_wrapping": false,
                "auto_close_brackets": true
            }

            account = client.accounts.get('kevin.shi')
            result = account.set_edit_preferences(input_)

        :param input_: the EditPreferencesInfo entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-accounts.html#edit-preferences-info
        :return:
        """
        endpoint = f"/accounts/{self.username}/preferences.edit"
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def get_watched_projects(self):
        """
        Retrieves all projects a user is watching.

        :return:
        """
        endpoint = f"/accounts/{self.username}/watched.projects"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def modify_watched_projects(self, input_):
        """
        Add new projects to watch or update existing watched projects.
        Projects that are already watched by a user will be updated with the provided configuration.

        .. code-block:: python

            input_ = [
                {
                    "project": "Test Project 1",
                    "notify_new_changes": true,
                    "notify_new_patch_sets": true,
                    "notify_all_comments": true,
                }
            ]

            account = client.accounts.get('kevin.shi')
            result = account.modify_watched_projects(input_)

        :param input_: the ProjectWatchInfo entities as list
        :return:
        """
        endpoint = f"/accounts/{self.username}/watched.projects"
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.post(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def delete_watched_projects(self, input_):
        """
        Projects posted to this endpoint will no longer be watched.

        .. code-block:: python

            input_ = [
                {
                    "project": "Test Project 1",
                    "filter": "branch:master"
                }
            ]

            account = client.accounts.get('kevin.shi')
            result = account.delete_watched_projects(input_)

        :param input_: the watched projects as list
        :return:
        """
        endpoint = f"/accounts/{self.username}/watched.projects:delete"
        base_url = self.gerrit.get_endpoint_url(endpoint)
        self.gerrit.requester.post(
            base_url, json=input_, headers=self.gerrit.default_headers
        )

    def get_external_ids(self):
        """
        Retrieves the external ids of a user account.
        Only external ids belonging to the caller may be requested. Users that have Modify Account can request external
        ids that belong to other accounts.

        :return:
        """
        endpoint = f"/accounts/{self.username}/external.ids"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def delete_external_ids(self, input_):
        """
        Delete a list of external ids for a user account.
        Only external ids belonging to the caller may be deleted. Users that have Modify Account can delete external
        ids that belong to other accounts.

        .. code-block:: python

            input_ = [
                "mailto:john.doe@example.com"
            ]

            account = client.accounts.get('kevin.shi')
            result = account.delete_external_ids(input_)

        :param input_: the external ids as list
        :return:
        """
        endpoint = f"/accounts/{self.username}/external.ids:delete"
        base_url = self.gerrit.get_endpoint_url(endpoint)
        self.gerrit.requester.post(
            base_url, json=input_, headers=self.gerrit.default_headers
        )

    def list_contributor_agreements(self):
        """
        Gets a list of the user’s signed contributor agreements.

        :return:
        """
        endpoint = f"/accounts/{self.username}/agreements"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def sign_contributor_agreement(self, input_):
        """
        Signs a contributor agreement.

        .. code-block:: python

            input_ = {
                "name": "Individual"
            }
            account = client.accounts.get('kevin.shi')
            result = account.sign_contributor_agreement(input_)

        :param input_: the ContributorAgreementInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-accounts.html#contributor-agreement-input
        :return:
        """
        endpoint = f"/accounts/{self.username}/agreements"
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def delete_draft_comments(self, input_):
        """
        Deletes some or all of a user’s draft comments.

        .. code-block:: python

            input_ = {
                "query": "is:abandoned"
            }
            account = client.accounts.get('kevin.shi')
            result = account.delete_draft_comments(input_)

        :param input_: the DeleteDraftCommentsInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-accounts.html#delete-draft-comments-input
        :return:
        """
        endpoint = f"/accounts/{self.username}/drafts:delete"
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.post(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def index(self):
        """
        Adds or updates the account in the secondary index.

        :return:
        """
        endpoint = f"/accounts/{self.username}/index"
        self.gerrit.requester.post(self.gerrit.get_endpoint_url(endpoint))

    def get_default_starred_changes(self):
        """
        Gets the changes that were starred with the default star by the identified user account.

        :return:
        """
        endpoint = f"/accounts/{self.username}/starred.changes"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return [self.gerrit.changes.get(item.get("id")) for item in result]

    def put_default_star_on_change(self, id_):
        """
        Star a change with the default label.

        :param id_: change id
        :return:
        """
        endpoint = f"/accounts/{self.username}/starred.changes/{id_}"
        self.gerrit.requester.put(self.gerrit.get_endpoint_url(endpoint))

    def remove_default_star_from_change(self, id_):
        """
        Remove the default star label from a change. This stops notifications.

        :param id_: change id
        :return:
        """
        endpoint = f"/accounts/{self.username}/starred.changes/{id_}"
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))

    def get_starred_changes(self):
        """
        Gets the changes that were starred with any label by the identified user account.

        :return:
        """
        endpoint = f"/accounts/{self.username}/stars.changes"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return [self.gerrit.changes.get(item.get("id")) for item in result]

    def get_star_labels_from_change(self, id_):
        """
        Get star labels from a change.

        :param id_: change id
        :return:
        """
        endpoint = f"/accounts/{self.username}/stars.changes/{id_}"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def update_star_labels_on_change(self, id_, input_):
        """
        Update star labels on a change.

        .. code-block:: python

            input_ = {
                "add": ["blue", "red"],
                "remove": ["yellow"]
            }

            account = client.accounts.get('kevin.shi')
            change_id = "myProject~master~I8473b95934b5732ac55d26311a706c9c2bde9940"
            result = account.update_star_labels_on_change(change_id, input_)


        :param id_: change id
        :param input_: the StarsInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-accounts.html#stars-input
        :return:
        """
        endpoint = f"/accounts/{self.username}/stars.changes/{id_}"
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.post(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result
