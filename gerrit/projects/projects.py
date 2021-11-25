#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus
from gerrit.projects.project import GerritProject


class GerritProjects(object):
    def __init__(self, gerrit):
        self.gerrit = gerrit

    def list(self, is_all=False, limit=None, skip=None,
             pattern_dispatcher=None, project_type=None,
             description=False, branches=None):
        """
        Get list of all available projects accessible by the caller.

        :param is_all: boolean value, if True then all projects (including
                       hidden ones) will be added to the results
        :param limit: Int value that allows to limit the number of projects
                      to be included in the output results
        :param skip: Int value that allows to skip the given
                     number of projects from the beginning of the list
        :param pattern_dispatcher: Dict of pattern type with respective
                     pattern value: {('prefix'|'match'|'regex') : value}
        :param project_type: string value for type of projects to be fetched
                            ('code'|'permissions'|'all')
        :param description: boolean value, if True then description will be
                            added to the output result
        :param branches: List of names of branches as a string to limit the
                         results to the projects having the specified branches
                         and include the sha1 of the branches in the results

        :return:
        """
        pattern_types = {'prefix': 'p',
                         'match': 'm',
                         'regex': 'r'}

        p, v = None, None
        if pattern_dispatcher is not None and pattern_dispatcher:
            for item in pattern_types:
                if item in pattern_dispatcher:
                    p, v = pattern_types[item], pattern_dispatcher[item]
                    break
            else:
                raise ValueError("Pattern types can be either "
                                 "'prefix', 'match' or 'regex'.")

        params = {k: v for k, v in (('n', limit),
                                    ('S', skip),
                                    (p, v),
                                    ('type', project_type),
                                    ('b', branches)) if v is not None}
        params['all'] = int(is_all)
        params['d'] = int(description)

        endpoint = "/projects/"
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint), params)
        result = self.gerrit.decode_response(response)
        return result

    def search(self, query, limit=None, skip=None):
        """
        Queries projects visible to the caller. The query string must be provided by the query parameter.
        The start and limit parameters can be used to skip/limit results.

        query parameter
          * name:'NAME' Matches projects that have exactly the name 'NAME'.
          * parent:'PARENT' Matches projects that have 'PARENT' as parent project.
          * inname:'NAME' Matches projects that a name part that starts with 'NAME' (case insensitive).
          * description:'DESCRIPTION' Matches projects whose description contains 'DESCRIPTION', using a full-text search.
          * state:'STATE' Matches project’s state. Can be either 'active' or 'read-only'.

        :param query:
        :param limit: Int value that allows to limit the number of accounts
                      to be included in the output results
        :param skip: Int value that allows to skip the given
                     number of accounts from the beginning of the list
        :return:
        """
        params = {k: v for k, v in (('limit', limit), ('start', skip)) if v is not None}

        endpoint = "/projects/?query=%s" % query
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint), params)
        result = self.gerrit.decode_response(response)
        return result

    def get(self, project_name):
        """
        Retrieves a project.

        :param project_name: the name of the project
        :return:
        """
        endpoint = "/projects/%s" % quote_plus(project_name)
        response = self.gerrit.requester.get(self.gerrit.get_endpoint_url(endpoint))
        result = self.gerrit.decode_response(response)
        return GerritProject.parse(result, gerrit=self.gerrit)

    def create(self, project_name, input_):
        """
        Creates a new project.

        .. code-block:: python

            input_ = {
                "description": "This is a demo project.",
                "submit_type": "INHERIT",
                "owners": [
                  "MyProject-Owners"
                ]
            }
            project = gerrit.projects.create('MyProject', input_)

        :param project_name: the name of the project
        :param input_: the ProjectInput entity,
          https://gerrit-review.googlesource.com/Documentation/rest-api-projects.html#project-input

        :return:
        """
        endpoint = "/projects/%s" % quote_plus(project_name)
        base_url = self.gerrit.get_endpoint_url(endpoint)
        response = self.gerrit.requester.put(
            base_url, json=input_, headers=self.gerrit.default_headers
        )
        result = self.gerrit.decode_response(response)
        return GerritProject.parse(result, gerrit=self.gerrit)

    def delete(self, project_name):
        """
        Delete the project, requires delete-project plugin

        :param project_name: project name
        :return:
        """
        endpoint = "/projects/%s/delete-project~delete" % quote_plus(project_name)
        self.gerrit.requester.post(self.gerrit.get_endpoint_url(endpoint))
