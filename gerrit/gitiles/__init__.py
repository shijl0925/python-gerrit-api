#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi

class GerritGitiles(object):
    def __init__(self, gerrit):
        self.gerrit = gerrit
        self.endpoint = "/plugins/gitiles"

    def commit(self, project, commit):
        """Retrieves a commit."""
        params = {"format": "JSON"}

        return self.gerrit.get(self.endpoint + f"/{project}/+/{commit}", params=params)

    def commits(self, project, branch, commit=None):
        """query commit history"""
        params = {"format": "JSON"}
        if commit is not None:
            params.update({"s": commit})

        return self.gerrit.get(self.endpoint + f"/{project}/+log/{branch}", params=params)
