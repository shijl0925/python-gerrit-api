#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import os
import pytest


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


@pytest.fixture(scope="function")
def gitiles_client():
    from gitiles import GitilesClient
    gitilest_url = "https://gerrit.googlesource.com/"
    client = GitilesClient(gitilest_url)

    return client

