#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus

from gerrit.utils.models import BaseModel
from gerrit.utils.common import params_creator


class GerritProjectBranch(BaseModel):
    branch_prefix = "refs/heads/"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entity_name = "ref"
        self.endpoint = f"/projects/{self.project}/branches/{self.name}"

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
        return self.gerrit.get(self.endpoint + f"/files/{quote_plus(file)}/content")

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
        return self.gerrit.get(self.endpoint + "/mergeable", params=input_)

    def get_reflog(self):
        """
        Gets the reflog of a certain branch.

        :return:
        """
        return self.gerrit.get(self.endpoint + "/reflog")

    def delete(self):
        """
        Delete a branch.

        :return:
        """
        self.gerrit.delete(self.endpoint)


class GerritProjectBranches(object):
    branch_prefix = "refs/heads/"

    def __init__(self, project, gerrit):
        self.project = project
        self.gerrit = gerrit
        self.endpoint = f"/projects/{self.project}/branches"

    def list(self, pattern_dispatcher=None, limit=None, skip=None):
        """
        List the branches of a project.

        :param pattern_dispatcher: Dict of pattern type with respective
               pattern value: {('match'|'regex') : value}
        :param limit: Limit the number of branches to be included in the results.
        :param skip: Skip the given number of branches from the beginning of the list.
        :return:
        """
        params = params_creator((("n", limit), ("s", skip)),
                                {"match": "m", "regex": "r"}, pattern_dispatcher)

        return self.gerrit.get(self.endpoint + "/", params=params)

    def get(self, name):
        """
        get a branch by ref

        :param name: branch ref name
        :return:
        """
        result = self.gerrit.get(self.endpoint + f"/{quote_plus(name)}")
        return GerritProjectBranch(json=result, project=self.project, gerrit=self.gerrit)

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
        return self.gerrit.put(
            self.endpoint + f"/{name}", json=input_, headers=self.gerrit.default_headers)

    def delete(self, name):
        """
        Delete a branch.

        :param name: branch ref name
        :return:
        """
        self.gerrit.delete(self.endpoint + f"/{quote_plus(name)}")
