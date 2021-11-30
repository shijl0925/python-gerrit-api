#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus

from gerrit.utils.models import BaseModel


class GerrirProjectTag(BaseModel):
    tag_prefix = "refs/tags/"

    def __init__(self, **kwargs):
        super(GerrirProjectTag, self).__init__(**kwargs)
        self.entity_name = "ref"

    @property
    def name(self):
        return self.ref.replace(self.tag_prefix, "")

    def delete(self):
        """
        Delete a tag.

        :return:
        """
        endpoint = "/projects/%s/tags/%s" % (self.project, self.name)
        self.gerrit.requester.delete(self.gerrit.get_endpoint_url(endpoint))


class GerrirProjectTags(object):
    tag_prefix = "refs/tags/"

    def __init__(self, project, gerrit):
        self.project = project
        self.gerrit = gerrit

    def list(self, pattern_dispatcher=None, limit=None, skip=None):
        """
        List the tags of a project.

        :param pattern_dispatcher: Dict of pattern type with respective
               pattern value: {('match'|'regex') : value}
        :param limit: Limit the number of tags to be included in the results.
        :param skip: Skip the given number of tags from the beginning of the list.
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
        endpoint = "/projects/{}/tags/".format(self.project)
        response = self.gerrit.requester.get(
            self.gerrit.get_endpoint_url(endpoint), params
        )
        result = self.gerrit.decode_response(response)
        return result

    def get(self, name):
        """
        get a tag by ref

        :param name: the tag ref
        :return:
        """
        endpoint = "/projects/%s/tags/%s" % (self.project, quote_plus(name))
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return GerrirProjectTag.parse(result, project=self.project, gerrit=self.gerrit)

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
        endpoint = "/projects/%s/tags/%s" % (self.project, name)
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return result

    def delete(self, name):
        """
        Delete a tag.

        :param name: the tag ref
        :return:
        """
        endpoint = "/projects/%s/tags/%s" % (self.project, quote_plus(name))
        base_url = self.gerrit.get_endpoint_url(endpoint)
        self.gerrit.requester.delete(base_url)
