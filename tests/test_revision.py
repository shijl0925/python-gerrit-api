#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import logging
import pytest

logger = logging.getLogger(__name__)


def test_get_change_revision(gerrit_client):
    change_id = "LineageOS%2Fandroid~lineage-20.0~I0bcf3ba13177947a2c018d9dcebdb94b561573d3"
    change = gerrit_client.changes.get(id_=change_id)

    c1 = change.get_revision(1).get_commit()
    assert c1.get("commit") == "530324a14d17c05a63dd8b003cba68f70f9f4a1e"

    c2 = change.get_revision().get_commit()
    assert c2.get("commit") == "1b16713d0ca30ecc9f6f3ac78554d57b5d4fa467"


def test_get_revision_actions(gerrit_client):
    change_id = "LineageOS%2Fandroid_kernel_xiaomi_sm8250~lineage-20~I53a2b78c6529e8459c6baacaba3f8c8dcaf0c387"
    change = gerrit_client.changes.get(id_=change_id)

    revision = change.get_revision()
    result = revision.get_revision_actions()

    assert "cherrypick" in result


def test_get_revision_review(gerrit_client):
    change_id = "LineageOS%2Fandroid_kernel_xiaomi_sm8250~lineage-20~I53a2b78c6529e8459c6baacaba3f8c8dcaf0c387"
    change = gerrit_client.changes.get(id_=change_id)

    revision = change.get_revision()
    result = revision.get_review()
    reviewers = result.get("reviewers")

    cc = reviewers.get("CC")
    assert len(cc) > 0

    reviewer = reviewers.get("REVIEWER")
    assert len(reviewer) > 0


def test_get_revision_related_changes(gerrit_client):
    change_id = "LineageOS%2Fandroid_device_fairphone_FP3~lineage-20~Ic54e2787ef27022556430c6c1db346b1e1348e39"
    change = gerrit_client.changes.get(id_=change_id)

    revision = change.get_revision()
    result = revision.get_related_changes()

    assert len(result.get("changes")) > 0


def test_get_revision_patch(gerrit_client):
    change_id = "LineageOS%2Fandroid_device_fairphone_FP3~lineage-20~Ic54e2787ef27022556430c6c1db346b1e1348e39"
    change = gerrit_client.changes.get(id_=change_id)

    revision = change.get_revision()
    content = revision.get_patch(decode=True)

    assert len(content) > 0


def test_get_revision_submit_type(gerrit_client):
    change_id = "LineageOS%2Fandroid_device_fairphone_FP3~lineage-20~Ic54e2787ef27022556430c6c1db346b1e1348e39"
    change = gerrit_client.changes.get(id_=change_id)

    revision = change.get_revision()
    result = revision.get_submit_type()

    assert result == "REBASE_IF_NECESSARY"


def test_get_revision_comments(gerrit_client):
    change_id = "LineageOS%2Fandroid_device_xiaomi_sdm710-common~lineage-20~I3767d8a44cbd9af891fbac7a67380b205b414a37"
    change = gerrit_client.changes.get(id_=change_id)

    revision = change.get_revision()
    comments = revision.comments.list()

    assert len(comments) > 0


def test_get_revision_comment(gerrit_client):
    change_id = "LineageOS%2Fandroid_device_xiaomi_sdm710-common~lineage-20~I3767d8a44cbd9af891fbac7a67380b205b414a37"
    change = gerrit_client.changes.get(id_=change_id)

    revision = change.get_revision()
    comment = revision.comments.get(id_="d297fbb3_7fd8fb52")

    assert "message" in comment.to_dict()


@pytest.mark.parametrize('reviewed, base, q, parent',
                         [(True, None, None, None),
                          (None, 1, None, None),
                          (None, None, "sdm710.mk", None),
                          (None, None, None, 1),
                          (None, None, None, None),
                          ])
def test_search_revision_files(gerrit_client, reviewed, base, q, parent):
    change_id = "LineageOS%2Fandroid_device_xiaomi_sdm710-common~lineage-20~I3767d8a44cbd9af891fbac7a67380b205b414a37"
    change = gerrit_client.changes.get(id_=change_id)

    revision = change.get_revision()
    revision.files.search(reviewed, base, q, parent)


def test_get_revision_files(gerrit_client):
    from gerrit.changes.revision.files import GerritChangeRevisionFile
    from gerrit.utils.exceptions import UnknownFile
    change_id = "LineageOS%2Fandroid_device_xiaomi_sdm710-common~lineage-20~I3767d8a44cbd9af891fbac7a67380b205b414a37"
    change = gerrit_client.changes.get(id_=change_id)

    revision = change.get_revision()
    files = revision.files
    assert len(files) > 0
    assert len(files.keys()) > 0
    assert "extract-files.sh" in files
    assert isinstance(files.get("extract-files.sh"), GerritChangeRevisionFile)

    for item in files:
        assert isinstance(item, GerritChangeRevisionFile)

    with pytest.raises(UnknownFile):
        revision.files["test.py"]


def test_get_revision_file(gerrit_client):
    change_id = "LineageOS%2Fandroid_device_xiaomi_sm8250-common~lineage-20~Icf55910aebae8d0ae519f0a0c20708aa81ae0bfc"
    change = gerrit_client.changes.get(id_=change_id)

    revision = change.get_revision()
    path = "overlay/frameworks/base/core/res/res/values/config.xml"
    file = revision.files[path]

    assert str(file) == path

    assert "path" in file.to_dict()

    assert len(file.get_content()) > 0
    assert len(file.get_content(decode=True)) > 0

    assert "content" in file.get_diff()
    assert len(file.get_blame()) > 0

    from gerrit.utils.exceptions import FileContentNotFoundError
    change_id = "LineageOS%2Fandroid_device_xiaomi_sdm710-common~lineage-20~I3767d8a44cbd9af891fbac7a67380b205b414a37"
    change = gerrit_client.changes.get(id_=change_id)

    revision = change.get_revision()
    path = "libshims/lib-imsvtshim.cpp"
    file = revision.files[path]
    with pytest.raises(FileContentNotFoundError):
        file.get_content()


def test_get_revision_votes(gerrit_client):
    change_id = "LineageOS%2Fandroid~lineage-20.0~I0bcf3ba13177947a2c018d9dcebdb94b561573d3"
    change = gerrit_client.changes.get(id_=change_id)

    revision = change.get_revision()
    votes = revision.list_votes(account="johnsonnolen")

    assert votes.get("Code-Review") == 1
    assert votes.get("Verified") == 1


def test_get_revision_reviewers(gerrit_client):
    change_id = "LineageOS%2Fandroid~lineage-20.0~I0bcf3ba13177947a2c018d9dcebdb94b561573d3"
    change = gerrit_client.changes.get(id_=change_id)

    revision = change.get_revision()
    result = revision.list_reviewers()
    assert len(result) > 0
