#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus

from gerrit.utils.models import BaseModel


class GerrirProjectCommit(BaseModel):
    def __init__(self, **kwargs):
        super(GerrirProjectCommit, self).__init__(**kwargs)
        self.entity_name = "commit"

    def get_include_in(self):
        """
        Retrieves the branches and tags in which a change is included.

        :return:
        """
        endpoint = "/projects/%s/commits/%s/in" % (self.project, self.commit)
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

    def get_file_content(self, file):
        """
        Gets the content of a file from a certain commit.

        :param file: the file path
        :return:
        """
        endpoint = "/projects/%s/commits/%s/files/%s/content" % (
            self.project,
            self.commit,
            quote_plus(file),
        )
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result

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
          https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#cherrypick-input
        :return:  the resulting cherry-picked change
        """
        endpoint = "/projects/%s/commits/%s/cherrypick" % (self.project, self.commit)
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.post(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return self.gerrit.changes.get(result.get("id"))

    def list_change_files(self):
        """
        Lists the files that were modified, added or deleted in a commit.

        :return:
        """
        endpoint = "/projects/%s/commits/%s/files/" % (self.project, self.commit)
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return result
