#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus

from gerrit.utils.models import BaseModel


class GerritProjectCommit(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entity_name = "commit"
        self.endpoint = f"/projects/{self.project}/commits/{self.commit}"

    def get_include_in(self):
        """
        Retrieves the branches and tags in which a change is included.

        :return:
        """
        return self.gerrit.get(self.endpoint + "/in")

    def get_file_content(self, file):
        """
        Gets the content of a file from a certain commit.

        :param file: the file path
        :return:
        """
        return self.gerrit.get(self.endpoint + f"/files/{quote_plus(file)}/content")

    def cherry_pick(self, input_):
        """
        Cherry-picks a commit of a project to a destination branch.

        .. code-block:: python

            input_ = {
                "message": "Implementing Feature X",
                "destination": "release-branch"
            }
            result = commit.cherry_pick(input_)

        :param input_: the CherryPickInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html
          #cherrypick-input
        :return:  the resulting cherry-picked change
        """
        result = self.gerrit.post(
            self.endpoint + "/cherrypick", json=input_, headers=self.gerrit.default_headers)
        return self.gerrit.changes.get(result.get("id"))

    def list_change_files(self):
        """
        Lists the files that were modified, added or deleted in a commit.

        :return:
        """
        return self.gerrit.get(self.endpoint + "/files/")
