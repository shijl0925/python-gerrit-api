#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

from gerrit.utils.models import BaseModel
from gerrit.utils.exceptions import UnknownBranch


class Branch(BaseModel):
    branch_prefix = "refs/heads/"

    def __init__(self, **kwargs):
        super(Branch, self).__init__(**kwargs)
        self.attributes = [
            "ref",
            "web_links",
            "revision",
            "can_delete",
            "project",
            "gerrit",
        ]

    @property
    def name(self):
        return self.ref.replace(self.branch_prefix, "")

    def get_file_content(self, file):
        """
        Gets the content of a file from the HEAD revision of a certain branch.
        The content is returned as base64 encoded string.

        :param file: the file path
        :return:
        """
        endpoint = "/projects/%s/branches/%s/files/%s/content" % (
            self.project,
            self.name,
            quote(file, safe=""),
        )
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def is_mergeable(self, input_):
        """
        Gets whether the source is mergeable with the target branch.

        .. code-block:: python

            input_ = {
                'source': 'testbranch',
                'strategy': 'recursive'
            }
            result = stable.is_mergeable(input_)
            print(result)

        :param input_: the MergeInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#merge-input
        :return:
        """
        endpoint = "/projects/%s/branches/%s/mergeable" % (self.project, self.name)
        response = self.gerrit.requester.get(
            self.gerrit.get_endpoint_url(endpoint), params=input_
        )
        result = self.gerrit.decode_response(response)
        return result

    def get_reflog(self):
        """
        Gets the reflog of a certain branch.

        :return:
        """
        endpoint = "/projects/%s/branches/%s/reflog" % (self.project, self.name)
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def delete(self):
        """
        Delete a branch.

        :return:
        """
        endpoint = "/projects/%s/branches/%s" % (self.project, self.name)
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))


class Branches(object):
    branch_prefix = "refs/heads/"

    def __init__(self, project, gerrit):
        self.project = project
        self.gerrit = gerrit
        self._data = []

    def poll(self):
        """

        :return:
        """
        endpoint = "/projects/%s/branches/" % self.project
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        for item in result:
            if item["ref"] == "refs/meta/config":
                result.remove(item)
        return result

    def iterkeys(self):
        """
        Iterate over the names of all available branches
        """
        if not self._data:
            self._data = self.poll()

        for row in self._data:
            yield row["ref"]

    def keys(self):
        """
        Return a list of the names of all branches
        """
        return list(self.iterkeys())

    def __len__(self):
        """

        :return:
        """
        return len(self.keys())

    def __contains__(self, ref):
        """
        True if ref exists in project
        """
        return ref in self.keys()

    def __getitem__(self, ref):
        """
        get a branch by ref

        :param ref: branch ref
        :return:
        """
        if not ref.startswith(self.branch_prefix):
            raise KeyError("branch ref should start with {}".format(self.branch_prefix))

        if not self._data:
            self._data = self.poll()

        result = [row for row in self._data if row["ref"] == ref]
        if result:
            return Branch.parse(result[0], project=self.project, gerrit=self.gerrit)
        else:
            raise UnknownBranch(ref)

    def __setitem__(self, key, value):
        """
        create a branch by ref
        :param key:
        :param value:
        :return:
        """
        if not key.startswith(self.branch_prefix):
            raise KeyError("branch ref should start with {}".format(self.branch_prefix))

        self.create(key.replace(self.branch_prefix, ""), value)

    def __delitem__(self, key):
        """
        Delete a branch by ref

        :param key:
        :return:
        """
        self[key].delete()

        # Reset to get it refreshed from Gerrit
        self._data = []

    def __iter__(self):
        """

        :return:
        """
        if not self._data:
            self._data = self.poll()

        for row in self._data:
            yield Branch.parse(row, project=self.project, gerrit=self.gerrit)

    def get(self, name):
        """
        get a branch by ref

        :param name: branch ref name
        :return:
        """
        return self[name]

    def create(self, name, input_):
        """
        Creates a new branch.

        .. code-block:: python

            input_ = {
                'revision': '76016386a0d8ecc7b6be212424978bb45959d668'
            }
            project = gerrit.projects.get('myproject')
            new_branch = project.branches.create('stable', input_)


        :param name: the branch name
        :param input_: the BranchInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-projects.html#branch-info
        :return:
        """
        ref = self.branch_prefix + name
        if ref in self.keys():
            return self[ref]

        endpoint = "/projects/%s/branches/%s" % (self.project, name)
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)

        # Reset to get it refreshed from Gerrit
        self._data = []

        return Branch.parse(result, project=self.project, gerrit=self.gerrit)

    def delete(self, name):
        """
        Delete a branch.

        :param name: branch ref name
        :return:
        """
        self[name].delete()

        # Reset to get it refreshed from Gerrit
        self._data = []
