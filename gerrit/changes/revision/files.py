#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus

from gerrit.utils.models import BaseModel
from gerrit.utils.exceptions import UnknownFile


class GerritChangeRevisionFile(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entity_name = "path"
        self.endpoint = f"/changes/{self.change}/revisions/{self.revision}" \
                        f"/files/{quote_plus(self.path)}"

    def get_content(self):
        """
        Gets the content of a file from a certain revision.
        The content is returned as base64 encoded string.

        :return:
        """
        return self.gerrit.get(self.endpoint + "/content")

    def download_content(self):
        """
        Downloads the content of a file from a certain revision, in a safe format that poses no
        risk for inadvertent execution of untrusted code.

        If the content type is defined as safe, the binary file content is returned verbatim.
        If the content type is not safe, the file is stored inside a ZIP file, containing a
        single entry with a random, unpredictable name having the same base and suffix as the
        true filename. The ZIP file is returned in verbatim binary form.

        :return:
        """
        return self.gerrit.get(self.endpoint + "/download")

    def get_diff(self, intraline=False):
        """
        Gets the diff of a file from a certain revision.

        :param intraline: If the intraline parameter is specified, intraline differences are
        included in the diff.
        :return:
        """
        endpoint = self.endpoint + "/diff"
        if intraline:
            endpoint += endpoint + "?intraline"

        return self.gerrit.get(endpoint)

    def get_blame(self):
        """
        Gets the blame of a file from a certain revision.

        :return:
        """
        return self.gerrit.get(self.endpoint + "/blame")

    def set_reviewed(self):
        """
        Marks a file of a revision as reviewed by the calling user.

        :return:
        """
        self.gerrit.put(self.endpoint + "/reviewed")

    def delete_reviewed(self):
        """
        Deletes the reviewed flag of the calling user from a file of a revision.

        :return:
        """
        self.gerrit.delete(self.endpoint + "/reviewed")


class GerritChangeRevisionFiles(object):
    def __init__(self, change, revision, gerrit):
        self.change = change
        self.revision = revision
        self.gerrit = gerrit
        self._data = []
        self.endpoint = f"/changes/{self.change}/revisions/{self.revision}/files"

    def poll(self):
        """

        :return:
        """
        result = self.gerrit.get(self.endpoint)
        files = []
        for key, value in result.items():
            file = value
            file.update({"path": key})
            files.append(file)

        return files

    def iterkeys(self):
        """
        Iterate over the paths of all files

        :return:
        """
        if not self._data:
            self._data = self.poll()

        for file in self._data:
            yield file["path"]

    def keys(self):
        """
        Return a list of the file paths

        :return:
        """
        return list(self.iterkeys())

    def __len__(self):
        """

        :return:
        """
        return len(self.keys())

    def __contains__(self, ref):
        """

        :param ref:
        :return:
        """
        return ref in self.keys()

    def __iter__(self):
        """

        :return:
        """
        if not self._data:
            self._data = self.poll()

        for file in self._data:
            yield GerritChangeRevisionFile.parse(
                file, change=self.change, revision=self.revision, gerrit=self.gerrit
            )

    def __getitem__(self, path):
        """
        get a file by path

        :param path: file path
        :return:
        """
        if not self._data:
            self._data = self.poll()

        result = [file for file in self._data if file["path"] == path]
        if result:
            return GerritChangeRevisionFile.parse(
                result[0],
                change=self.change,
                revision=self.revision,
                gerrit=self.gerrit,
            )
        else:
            raise UnknownFile(path)

    def get(self, path):
        """
        get a file by path

        :param path: file path
        :return:
        """
        return self[path]
