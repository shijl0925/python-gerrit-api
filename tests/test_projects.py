#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import logging
import pytest

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(module)s %(levelname)s: %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S')


@pytest.fixture(scope="function")
def gerrit_client():
    from gerrit import GerritClient
    gerrit_url = "https://gerrit-review.googlesource.com/"
    client = GerritClient(gerrit_url)
    return client


def test_list_projects(gerrit_client):
    resp = gerrit_client.projects.list(limit=25, skip=0)

    assert len(resp) > 0


def test_search_projects(gerrit_client):
    query = "name:git-repo"
    resp = gerrit_client.projects.search(query=query, limit=25, skip=0)

    assert len(resp) == 1


def test_get_project(gerrit_client):
    from gerrit.projects.project import GerritProject
    project_name = "git-repo"
    project = gerrit_client.projects.get(name=project_name)

    assert project.name == project_name
