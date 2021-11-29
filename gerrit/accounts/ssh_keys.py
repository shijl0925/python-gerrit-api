#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from gerrit.utils.models import BaseModel


class GerritAccountSSHKey(BaseModel):
    def __init__(self, **kwargs):
        super(GerritAccountSSHKey, self).__init__(**kwargs)
        self.entity_name = "seq"

    def delete(self):
        """
        Deletes an SSH key of a user.

        :return:
        """
        endpoint = "/accounts/%s/sshkeys/%s" % (self.username, self.seq)
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))


class GerritAccountSSHKeys(object):
    def __init__(self, username, gerrit):
        self.username = username
        self.gerrit = gerrit

    def list(self):
        """
        Returns the SSH keys of an account.

        :return:
        """
        endpoint = "/accounts/%s/sshkeys" % self.username
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return GerritAccountSSHKey.parse_list(
            result, username=self.username, gerrit=self.gerrit
        )

    def get(self, seq):
        """
        Retrieves an SSH key of a user.

        :param seq: SSH key id
        :return:
        """
        endpoint = "/accounts/%s/sshkeys/%s" % (self.username, str(seq))
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return GerritAccountSSHKey.parse(
            result, username=self.username, gerrit=self.gerrit
        )

    def add(self, ssh_key):
        """
        Adds an SSH key for a user.
        The SSH public key must be provided as raw content in the request body.

        :param ssh_key: SSH key raw content
        :return:
        """
        endpoint = "/accounts/%s/sshkeys" % self.username
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.post(
            base_url, data=ssh_key, headers={"Content-Type": "plain/text"}
        )
        result = self.gerrit.decode_response(response)
        return GerritAccountSSHKey.parse(
            result, username=self.username, gerrit=self.gerrit
        )

    def delete(self, seq):
        """
        Deletes an SSH key of a user.

        :param seq: SSH key id
        :return:
        """
        endpoint = "/accounts/%s/sshkeys/%s" % (self.username, str(seq))
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))
