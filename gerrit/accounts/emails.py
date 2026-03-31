#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from typing import Any
import logging
import requests
from gerrit import GerritClient
from gerrit.utils.gerritbase import GerritBase
from gerrit.utils.exceptions import (
    AccountEmailNotFoundError,
    AccountEmailAlreadyExistsError,
    GerritAPIException,
)


logger = logging.getLogger(__name__)


class GerritAccountEmail(GerritBase):
    def __init__(self, email: str, account: Any, gerrit: GerritClient) -> None:
        self.email = email
        self.account = account
        self.gerrit = gerrit
        self.endpoint = f"/accounts/{self.account}/emails/{self.email}"
        super().__init__()

    def __str__(self) -> str:
        return self.email

    def delete(self) -> None:
        """
        Deletes an email address of an account.

        :return:
        """
        self.gerrit.delete(self.endpoint)

    def set_preferred(self) -> None:
        """
        Sets an email address as preferred email address for an account.

        :return:
        """
        self.gerrit.put(self.endpoint + "/preferred")


class GerritAccountEmails:
    def __init__(self, account: Any, gerrit: GerritClient) -> None:
        self.account = account
        self.gerrit = gerrit
        self.endpoint = f"/accounts/{self.account}/emails"

    def list(self) -> Any:
        """
        Returns the email addresses that are configured for the specified user.

        :return:
        """
        result = self.gerrit.get(self.endpoint)
        return result

    def create(self, email, input_=None) -> Any:
        """
        Registers a new email address for the user.

        .. code-block:: python

            input_ = {
                "email": "john.doe@example.com",
                "preferred": False,
                "no_confirmation": False
            }
            account = client.accounts.get('kevin.shi')
            result = account.emails.create('john.doe@example.com', input_)

        :param email: the email address to register
        :param input_: the EmailInput entity (optional),
          https://gerrit-review.googlesource.com/Documentation/rest-api-accounts.html#email-input
        :return:
        """
        try:
            self.get(email)
            message = f"Account Email {email} already register"
            logger.error(message)
            raise AccountEmailAlreadyExistsError(message)
        except AccountEmailNotFoundError:
            if input_ is not None:
                self.gerrit.put(
                    self.endpoint + f"/{email}",
                    json=input_,
                    headers=self.gerrit.default_headers,
                )
            else:
                self.gerrit.put(self.endpoint + f"/{email}")
            return self.get(email)

    def get(self, email) -> Any:
        """
        Retrieves an email address of a user.

        :return:
        """
        try:
            result = self.gerrit.get(self.endpoint + f"/{email}")

            email_ = result.get("email")
            return GerritAccountEmail(
                email=email_, account=self.account, gerrit=self.gerrit
            )
        except requests.exceptions.HTTPError as error:
            if error.response.status_code == 404:
                message = f"Account Email {email} does not exist"
                raise AccountEmailNotFoundError(message)
            raise GerritAPIException from error

    def set_preferred(self, email) -> None:
        """
        Sets an email address as preferred email address for an account.

        :param email: account email
        :return:
        """
        self.get(email)
        self.gerrit.put(self.endpoint + f"/{email}/preferred")

    def delete(self, email) -> None:
        """
        Deletes an email address of an account.

        :param email: account email
        :return:
        """
        self.get(email)
        self.gerrit.delete(self.endpoint + f"/{email}")
