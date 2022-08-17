#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from gerrit.utils.common import params_creator
try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus

from gerrit.utils.models import BaseModel


class GerritProjectTag(BaseModel):
    tag_prefix = "refs/tags/"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entity_name = "ref"
        self.endpoint = f"/projects/{self.project}/tags"

    @property
    def name(self):
        return self.ref.replace(self.tag_prefix, "")

    def delete(self):
        """
        Delete a tag.

        :return:
        """
        self.gerrit.delete(self.endpoint + f"/{self.name}")


class GerritProjectTags(object):
    tag_prefix = "refs/tags/"

    def __init__(self, project, gerrit):
        self.project = project
        self.gerrit = gerrit
        self.endpoint = f"/projects/{self.project}/tags"

    def list(self, pattern_dispatcher=None, limit=None, skip=None):
        """
        List the tags of a project.

        :param pattern_dispatcher: Dict of pattern type with respective
               pattern value: {('match'|'regex') : value}
        :param limit: Limit the number of tags to be included in the results.
        :param skip: Skip the given number of tags from the beginning of the list.
        :return:
        """
        params = params_creator((("n", limit), ("s", skip)),
                                {"match": "m", "regex": "r"}, pattern_dispatcher)
        return self.gerrit.get(self.endpoint + "/", params=params)

    def get(self, name):
        """
        get a tag by ref

        :param name: the tag ref
        :return:
        """
        result = self.gerrit.get(self.endpoint + f"/{quote_plus(name)}")
        return GerritProjectTag(json=result, project=self.project, gerrit=self.gerrit)

    def create(self, name, input_):
        """
        Creates a new tag on the project.

        .. code-block:: python

            input_ = {
                "message": "annotation",
                'revision': 'c83117624b5b5d8a7f86093824e2f9c1ed309d63'
            }

            project = client.projects.get('myproject')
            new_tag = project.tags.create('1.1.8', input_)

        :param name: the tag name
        :param input_: the TagInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-projects.html#tag-input
        :return:
        """
        return self.gerrit.put(
            self.endpoint + f"/{name}", json=input_, headers=self.gerrit.default_headers)

    def delete(self, name):
        """
        Delete a tag.

        :param name: the tag ref
        :return:
        """
        self.gerrit.delete(self.endpoint + f"/{quote_plus(name)}")
