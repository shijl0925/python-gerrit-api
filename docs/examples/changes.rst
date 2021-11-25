===========
api/cahnges
===========

Examples
--------

setup gerrit client::

    from gerrit import GerritClient
    gerrit = GerritClient(base_url="https://yourgerrit", username='******', password='xxxxx')

Queries changes.::

    result = gerrit.changes.search('q=status:open')

Retrieves a change.::

    change = gerrit.changes.get(
        "MyProject~master~I39b027b763fb0b0dc7ed6c9e6bb5128d882dbe7c"
    )

create a change.::

    input_ = {
        "project": "myProject",
        "subject": "Let's support 100% Gerrit workflow direct in browser",
        "branch": "stable",
        "topic": "create-change-in-browser",
        "status": "NEW"
    }
    result = gerrit.changes.create(input_)

Deletes a change.::

    gerrit.changes.delete("MyProject~master~I39b027b763fb0b0dc7ed6c9e6bb5128d882dbe7c")

