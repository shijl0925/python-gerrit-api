#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import logging

logger = logging.getLogger(__name__)


def test_get_commit(gitiles_client):
    repo = "gitiles"
    hash = "baaf2895e0732228c84a07620fffe57e4ff47f03"
    res = gitiles_client.commit(repo, commit=hash)

    assert "commit" in res
    assert "author" in res
    assert "message" in res


def test_list_commits(gitiles_client):
    repo = "gitiles"
    branch = "refs/heads/master"
    hash = "baaf2895e0732228c84a07620fffe57e4ff47f03"
    res = gitiles_client.commits(repo, branch, start=hash)

    assert "next" in res
    assert "log" in res
    assert len(res.get("log")) > 0


def test_download_file(gitiles_client):
    repo = "buck"
    ref = "refs/heads/master"
    path = "scripts/travisci_install_android_sdk.sh"

    content = gitiles_client.download_file(repo, ref, path)
    from base64 import b64decode
    assert len(b64decode(content).decode("utf-8")) > 0

    content = gitiles_client.download_file(repo, ref, path, decode=True)
    assert len(content) > 0
