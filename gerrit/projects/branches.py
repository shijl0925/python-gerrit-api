#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus

from gerrit.utils.models import BaseModel


class GerrirProjectBranch(BaseModel):
    branch_prefix = "refs/heads/"

    def __init__(self, **kwargs):
        super(GerrirProjectBranch, self).__init__(**kwargs)
        self.entity_name = "ref"

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
            quote_plus(file),
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


class GerrirProjectBranches(object):
    branch_prefix = "refs/heads/"

    def __init__(self, project, gerrit):
        self.project = project
        self.gerrit = gerrit

    def list(self, pattern_dispatcher=None, limit=None, skip=None):
        """
        List the branches of a project.

        :param pattern_dispatcher: Dict of pattern type with respective
               pattern value: {('match'|'regex') : value}
        :param limit: Limit the number of branches to be included in the results.
        :param skip: Skip the given number of branches from the beginning of the list.
        :return:
        """
        pattern_types = {"match": "m", "regex": "r"}

        p, v = None, None
        if pattern_dispatcher is not None and pattern_dispatcher:
            for item in pattern_types:
                if item in pattern_dispatcher:
                    p, v = pattern_types[item], pattern_dispatcher[item]
                    break
            else:
                raise ValueError("Pattern types can be either 'match' or 'regex'.")

        params = {k: v for k, v in (("n", limit), ("s", skip), (p, v)) if v is not None}
        endpoint = "/projects/%s/branches/" % self.project
        response = self.gerrit.requester.get(
            self.gerrit.get_endpoint_url(endpoint), params
        )
        result = self.gerrit.decode_response(response)
        return result

    def get(self, name):
        """
        get a branch by ref

        :param name: branch ref name
        :return:
        """
        endpoint = "/projects/%s/branches/%s" % (self.project, quote_plus(name))
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return GerrirProjectBranch.parse(
            result, project=self.project, gerrit=self.gerrit
        )

    def create(self, name, input_):
        """
        Creates a new branch.

        .. code-block:: python

            input_ = {
                'revision': '76016386a0d8ecc7b6be212424978bb45959d668'
            }
            project = client.projects.get('myproject')
            new_branch = project.branches.create('stable', input_)


        :param name: the branch name
        :param input_: the BranchInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-projects.html#branch-info
        :return:
        """
        endpoint = "/projects/%s/branches/%s" % (self.project, name)
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def delete(self, name):
        """
        Delete a branch.

        :param name: branch ref name
        :return:
        """
        endpoint = "/projects/%s/branches/%s" % (self.project, quote_plus(name))
        base_url = self.gerrit.get_endpoint_url(endpoint)
        self.gerrit.requester.delete(base_url)
