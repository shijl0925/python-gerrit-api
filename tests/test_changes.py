#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import logging
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.parametrize('query, options, limit, skip',
                         [("status:open", None, 25, 0),
                          ("project:LineageOS/android+status:merged", None, 25, 0),
                          ("project:LineageOS/android", ["LABELS", "DETAILED_ACCOUNTS"], 25, 0)
                          ])
def test_search_changes(gerrit_client, query, options, limit, skip):
    resp = gerrit_client.changes.search(query=query, options=options, limit=limit, skip=skip)

    assert len(resp) >= 1


@pytest.mark.xfail(reason="Request is not authorized")
def test_create_change(gerrit_client):
    input_ = {
        "project": "LineageOS/android",
        "subject": "Let's support 100% Gerrit workflow direct in browser",
        "branch": "lineage-20.0",
        "topic": "create-change-in-browser",
        "status": "NEW"
    }
    gerrit_client.changes.create(input_)


def test_get_change(gerrit_client, latest_change_id):
    from gerrit.utils.exceptions import ChangeNotFoundError
    with pytest.raises(ChangeNotFoundError):
        gerrit_client.changes.get(id_="I00000000")

    with pytest.raises(ChangeNotFoundError):
        gerrit_client.changes.get(id_="I0bcf3ba13177947a2c018d9dcebdb94b561573d3")

    change = gerrit_client.changes.get(id_=latest_change_id)

    assert "_number" in change.to_dict()

    logger.debug(change.to_dict())

    attrs = ["id", "project", "branch", "hashtags", "change_id", "subject",
             "status", "created", "updated", "number", "owner", "insertions", "deletions"]
    for attr in attrs:
        logger.debug(f"{attr}, {hasattr(change, attr)}, {getattr(change, attr)}")

    assert all([hasattr(change, attr) for attr in attrs])


@pytest.mark.xfail(reason="Request is not authorized")
def test_delete_change(gerrit_client):
    change_id = "LineageOS%2Fandroid~lineage-20.0~I07827e3af3827a40260f012e828a96dbf4dfcbe1"
    gerrit_client.changes.delete(id_=change_id)


def test_get_change_detail(gerrit_client, latest_change_id):
    change = gerrit_client.changes.get(id_=latest_change_id)

    detail = change.get_detail(options=["LABELS"])
    assert "labels" in detail


def test_get_change_votes(gerrit_client):
    change_id = "LineageOS%2Fandroid~lineage-20.0~I0bcf3ba13177947a2c018d9dcebdb94b561573d3"
    change = gerrit_client.changes.get(id_=change_id)

    votes = change.list_votes(account="johnsonnolen")

    assert votes.get("Code-Review") == 1
    assert votes.get("Verified") == 1


def test_get_change_topics(gerrit_client):
    change_id = "LineageOS%2Fandroid~lineage-20.0~I07827e3af3827a40260f012e828a96dbf4dfcbe1"
    change = gerrit_client.changes.get(id_=change_id)

    topic = change.get_topic()
    assert topic == "tangorpro"


def test_list_submitted_together_changes(gerrit_client, latest_change_id):
    change = gerrit_client.changes.get(id_=latest_change_id)

    res = change.list_submitted_together_changes()
    assert len(res.get("changes")) >= 0


def test_get_change_include_in(gerrit_client, latest_change_id):
    change = gerrit_client.changes.get(id_=latest_change_id)

    res = change.get_include_in()

    assert "branches" in res
    assert "tags" in res


def test_list_change_comments(gerrit_client, latest_change_id):
    change = gerrit_client.changes.get(id_=latest_change_id)

    res = change.list_comments()
    assert len(res.keys()) >= 0


def test_get_change_attention_set(gerrit_client, latest_change_id):
    change = gerrit_client.changes.get(id_=latest_change_id)

    res = change.get_attention_set()
    assert len(res) >= 0


def test_get_change_hashtags(gerrit_client, latest_change_id):
    change = gerrit_client.changes.get(id_=latest_change_id)

    res = change.get_hashtags()
    assert len(res) >= 0


def test_get_change_meta_diff(gerrit_client, latest_change_id):
    change = gerrit_client.changes.get(id_=latest_change_id)
    res = change.get_meta_diff()

    assert "removed" in res
    assert "added" in res


def test_get_change_messages(gerrit_client, latest_change_id):
    change = gerrit_client.changes.get(id_=latest_change_id)

    messages = change.messages.list()
    assert len(messages) >= 0


def test_get_change_message(gerrit_client):
    change_id = "LineageOS%2Fandroid_device_xiaomi_sdm710-common~lineage-20~I3767d8a44cbd9af891fbac7a67380b205b414a37"
    change = gerrit_client.changes.get(id_=change_id)

    message = change.messages.get(id_="47aa7615e1759c79a182f82003b2b295cdbe9ca2")
    assert "message" in message.to_dict()


def test_get_change_reviewers(gerrit_client, latest_change_id):
    change = gerrit_client.changes.get(id_=latest_change_id)

    reviewers = change.reviewers.list()
    assert len(reviewers) >= 0


def test_get_change_reviewer(gerrit_client):
    change_id = "LineageOS%2Fandroid~lineage-20.0~I0bcf3ba13177947a2c018d9dcebdb94b561573d3"
    change = gerrit_client.changes.get(id_=change_id)

    from gerrit.utils.exceptions import ReviewerNotFoundError
    with pytest.raises(ReviewerNotFoundError):
        change.reviewers.get(account="shijl0925")

    reviewer = change.reviewers.get(account="javelinanddart")
    assert "_account_id" in reviewer.to_dict()

    votes = reviewer.list_votes()
    assert votes.get("Code-Review") == 2


@pytest.mark.xfail(reason="Request is not authorized")
def test_add_change_reviewer(gerrit_client):
    change_id = "LineageOS%2Fandroid~lineage-20.0~I0bcf3ba13177947a2c018d9dcebdb94b561573d3"
    change = gerrit_client.changes.get(id_=change_id)

    from gerrit.utils.exceptions import ReviewerAlreadyExistsError
    with pytest.raises(ReviewerAlreadyExistsError):
        change.reviewers.add(input_={"reviewer": "javelinanddart"})

    change.reviewers.add(input_={"reviewer": "jialiang.shi"})
