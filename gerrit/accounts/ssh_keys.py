#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from gerrit.utils.models import BaseModel


class GerritAccountSSHKey(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entity_name = "seq"
        self.endpoint = f"/accounts/{self.username}/sshkeys"

    def delete(self):
        """
        Deletes an SSH key of a user.

        :return:
        """
        self.gerrit.delete(self.endpoint + f"/{str(self.seq)}")


class GerritAccountSSHKeys(object):
    def __init__(self, username, gerrit):
        self.username = username
        self.gerrit = gerrit
        self.endpoint = f"/accounts/{self.username}/sshkeys"

    def list(self):
        """
        Returns the SSH keys of an account.

        :return:
        """
        result = self.gerrit.get(self.endpoint)
        return GerritAccountSSHKey.parse_list(result, username=self.username, gerrit=self.gerrit)

    def get(self, seq):
        """
        Retrieves an SSH key of a user.

        :param seq: SSH key id
        :return:
        """
        result = self.gerrit.get(self.endpoint + f"/{str(seq)}")
        return GerritAccountSSHKey(json=result, username=self.username, gerrit=self.gerrit)

    def add(self, ssh_key):
        """
        Adds an SSH key for a user.
        The SSH public key must be provided as raw content in the request body.

        :param ssh_key: SSH key raw content
        :return:
        """
        result = self.gerrit.post(self.endpoint,
                                  data=ssh_key, headers={"Content-Type": "plain/text"})
        return GerritAccountSSHKey(json=result, username=self.username, gerrit=self.gerrit)

    def delete(self, seq):
        """
        Deletes an SSH key of a user.

        :param seq: SSH key id
        :return:
        """
        self.gerrit.delete(self.endpoint + f"/{str(seq)}")
