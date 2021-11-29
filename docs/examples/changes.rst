===========
api/changes
===========

Examples
--------

setup gerrit client::

    from gerrit import GerritClient
    gerrit = GerritClient(base_url="https://yourgerrit", username='******', password='xxxxx')

Queries changes.::

    result = gerrit.changes.search(query=['status:open'])
    # or
    query = ["is:open+owner:self", "is:open+reviewer:self+-owner:self", "is:closed+owner:self+limit:5"]
    result = gerrit.changes.search(query=query, options=["LABELS"])

Retrieves a change.::

    change = gerrit.changes.get("MyProject~master~I39b027b763fb0b0dc7ed6c9e6bb5128d882dbe7c")

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
    # or
    change = gerrit.changes.get("MyProject~master~I39b027b763fb0b0dc7ed6c9e6bb5128d882dbe7c")
    change.delete()
