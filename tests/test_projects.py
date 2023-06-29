#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import os
import pytest


# @pytest.fixture(scope="function")
# def gerrit_client():
#     from gerrit import GerritClient
#     gerrit_url = "https://gerrit-review.googlesource.com/"
#     client = GerritClient(gerrit_url)
#     return client


@pytest.fixture(scope="function")
def gerrit_client():
    from gerrit import GerritClient


    gerrit_url = os.getenv("GERRIT_HOST_URL")
    username = os.getenv("GERRIT_USERNAME")
    password = os.getenv("GERRIT_PASSWORD")

    if not username:
        raise ValueError("GERRIT_USERNAME not found in environment variables")
    
    if not password:
        raise ValueError("GERRIT_PASSWORD not found in environment variables")
    
    if not gerrit_url:
        raise ValueError("GERRIT_HOST_URL not found in environment variables")

    client = GerritClient(
        base_url=gerrit_url,
        username=username,
        password=password,
        timeout=10,
        max_retries=3
    )
    return client


def test_list_projects(gerrit_client):
    resp = gerrit_client.projects.list(limit=25, skip=0)

    assert len(resp) > 0


def test_search_projects(gerrit_client):
    query = "name:LineageOS/android"
    resp = gerrit_client.projects.search(query=query, limit=25, skip=0)

    assert len(resp) == 1


def test_get_project(gerrit_client):
    project_name = "LineageOS/android"
    project = gerrit_client.projects.get(name=project_name)

    assert project.name == project_name
