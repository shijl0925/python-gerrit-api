===========
api/change
===========

Examples
--------

setup gerrit client and retrieve one change instance::

    from gerrit import GerritClient
    gerrit = GerritClient(base_url="https://yourgerrit", username='******', password='xxxxx')

    change = gerrit.changes.get(
        "MyProject~master~I39b027b763fb0b0dc7ed6c9e6bb5128d882dbe7c"
    )

Update an existing change by using a MergePatchSetInput entity.::

    input_ = {
        "subject": "Merge master into stable",
        "merge": {
          "source": "refs/heads/master"
        }
    }

    result = change.update(input_)

Creates a new patch set with a new commit message.::

    input_ = {
        "message": "New Commit message \\n\\nChange-Id: I10394472cbd17dd12454f229e4f6de00b143a444\\n"
    }

    result = change.set_commit_message(input_)

Retrieves the topic of a change.::

    topic = change.get_topic()

Sets the topic of a change.::

    topic = change.set_topic("test topic")

Deletes the topic of a change.::

    change.delete_topic()

Retrieves the account of the user assigned to a change.::

    assignee = change.get_assignee()

Sets the assignee of a change.::

    input_ = {
        "assignee": "jhon.doe"
    }
    result = change.set_assignee(input_)

Returns a list of every user ever assigned to a change, in the order in which they were first assigned.:

    result = change.get_past_assignees()

Deletes the assignee of a change.::

    result = change.delete_assignee()

Abandons a change.::

    result = change.abandon()

Restores a change.::

    result = change.restore()

Deletes a change.::

    change.delete()

Marks the change to be private. Only open changes can be marked private.::

    input_ = {
        "message": "After this security fix has been released we can make it public now."
    }
    change.mark_private(input_)

Marks the change to be non-private. Note users can only unmark own private changes.::

    input_ = {
        "message": "This is a security fix that must not be public."
    }
    change.unmark_private(input_)
    # or
    change.unmark_private()

get one revision by revision id.::

    revision = change.get_revision("534b3ce21655a092eccf72680f2ad16b8fecf119")

