Project description
===================

.. image:: https://img.shields.io/pypi/pyversions/python-gerrit-api.svg
    :target: https://pypi.python.org/pypi/python-gerrit-api
.. image:: https://img.shields.io/pypi/v/python-gerrit-api.svg
    :target: https://pypi.python.org/pypi/python-gerrit-api
.. image:: https://static.pepy.tech/badge/python-gerrit-api
    :target: https://pepy.tech/project/python-gerrit-api
.. image:: https://sonarcloud.io/api/project_badges/measure?project=shijl0925_python-gerrit-api&metric=alert_status
    :target: https://sonarcloud.io/dashboard?id=shijl0925_python-gerrit-api
.. image:: https://sonarcloud.io/api/project_badges/measure?project=shijl0925_python-gerrit-api&metric=coverage
    :target: https://sonarcloud.io/summary/overall?id=shijl0925_python-gerrit-api
.. image:: https://codecov.io/gh/shijl0925/python-gerrit-api/branch/master/graph/badge.svg?token=HU6U2LNHUK 
    :target: https://codecov.io/gh/shijl0925/python-gerrit-api
.. image:: https://app.codacy.com/project/badge/Grade/fb3a59e09af8422ca2349b3974e02833
    :target: https://app.codacy.com/gh/shijl0925/python-gerrit-api/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade
.. image:: https://app.codacy.com/project/badge/Coverage/fb3a59e09af8422ca2349b3974e02833
    :target: https://app.codacy.com/gh/shijl0925/python-gerrit-api/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage
.. image:: https://img.shields.io/github/license/shijl0925/python-gerrit-api.svg
    :target: LICENSE
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

What is it?
-----------
python-gerrit-api provides a simple interface for clients to interact with Gerrit Code Review via the REST API.


Installation
------------

The easiest way to install the latest version is by using pip to pull it from PyPI.

Using Pip or Setuptools

.. code-block:: bash

	pip install python-gerrit-api

Or:

.. code-block:: bash

	easy_install python-gerrit-api


You may also use Git to clone the repository from Github and install it manually.

.. code-block:: bash

    git clone https://github.com/shijl0925/python-gerrit-api.git
    cd python-gerrit-api
    python setup.py install

Usage
-----

For a full documentation spec of what this library supports see `readthedocs
<https://python-gerrit-api.readthedocs.io/en/latest/>`_

Example 1: setup gerrit client:

.. code:: python

    from gerrit import GerritClient
    client = GerritClient(base_url="https://yourgerrit", username='******', password='xxxxx')

Example 2: operate gerrit project:

.. code:: python

    # Retrieves a project.
    project = client.projects.get('MyProject')

    # or
    project = client.get(endpoint="/projects/MyProject")

.. code:: python

    # Creates a new project.
    input_ = {
        "description": "This is a demo project.",
        "submit_type": "INHERIT",
        "owners": [
          "MyProject-Owners"
        ]
    }
    client.projects.create('MyProject', input_)

    # or
    client.post(endpoint="/projects/MyProject", json=input_)

.. code:: python

    # Sets the description of a project.
    project = client.projects.get('MyProject')
    input_ = {
        "description": "Plugin for Gerrit that handles the replication.",,
        "commit_message": "Update the project description"
    }
    result = project.set_description(input_)

    # or
    result = client.put(endpoint="/projects/MyProject/description", json=input_)

.. code:: python

    # Deletes the description of a project.
    project = client.projects.get('MyProject')
    project.delete_description()

    # or
    client.delete(endpoint="/projects/MyProject/description")

.. code:: python

    # get a branch of th project by ref
    branch = project.branches.get('refs/heads/stable')

.. code:: python

    # get these branches of th project
    branches = project.branches.list()

    # or 
    branches = client.get(endpoint = "/projects/MyProject"/branches/)

.. code:: python

    # Creates a new branch.
    input_ = {
        'revision': '76016386a0d8ecc7b6be212424978bb45959d668'
    }
    new_branch = project.branches.create('stable', input_)

    # or
    result = client.put(endpoint="/projects/MyProject/branches/stable", json=input_)


Example 3: operate gerrit change:

.. code:: python

    # Retrieves a change.
    change = client.changes.get('python-sonarqube-api~stable3~I60c3bf10a5b0daf62a0f7c38bdf90b15026bbc2e')

    # or
    change = client.get(endpoint='/changes/python-sonarqube-api~stable3~I60c3bf10a5b0daf62a0f7c38bdf90b15026bbc2e')

.. code:: python

    # Marks a change as reviewed.
    change.mark_as_reviewed()

.. code:: python

    # Adds and removes hashtags from a change.
    input_ = {
        "add" : [
            "hashtag3"
        ],
        "remove" : [
            "hashtag2"
        ]
    }
    result = change.set_hashtags(input_)

.. code:: python

    # get one revision by revision id
    revision = change.get_revision('534b3ce21655a092eccf72680f2ad16b8fecf119')

.. code:: python

    # get a file by path
    file = revision.files.get('sonarqube/community/favorites.py')

.. code:: python

    # Gets the diff of a file from a certain revision.
    file_diff = file.get_diff()

Example 4: operate gerrit account:

.. code:: python

    # Retrieves an account
    account = client.accounts.get('kevin.shi')

.. code:: python

    # Sets the full name of an account.
    input_ = {
        "name": "Keven Shi"
    }
    result = account.set_name(input_)

.. code:: python

    # Adds an SSH key for a user.
    ssh_key = 'ssh-rsa xxx'
    result = account.ssh_keys.add(ssh_key)

Example 5: operate gerrit group:

.. code:: python

    # Retrieves a group.
    group = client.groups.get('af01a8cb8cbd8ee7be072b98b1ee882867c0cf06')

.. code:: python

    # Adds a user as member to a Gerrit internal group.
    result = group.add_member("ci_jenkins")

.. code:: python

    # Sets the owner group of a Gerrit internal group.
    input_ = {
        "owner": "6a1e70e1a88782771a91808c8af9bbb7a9871389"
    }
    result = group.set_owner(input_)

About this library
-------------------
Gerrit is a code review and project management tool for Git based projects.

Gerrit makes reviews easier by showing changes in a side-by-side display, and allowing inline comments to be added by any reviewer.

Gerrit simplifies Git based project maintainership by permitting any authorized user to submit changes to the master Git repository, rather than requiring all approved changes to be merged in by hand by the project maintainer.

This library allows you to automate most common Gerrit operations using Python, such as:

* Ability to create/delete/query Gerrit projects, and ability to execute project:
    * Retrieves/Set/Delete the description of a project.
    * Retrieves the name of a project's parent project, and set the parent project for a project.
    * Retrieves for a project the name of the branch to which HEAD points, and sets HEAD for a project.
    * Gets some configuration information about a project, and sets the configuration of a project.
    * Lists the access rights for a single project, and sets access rights for a project.
    * Retrieves a commit of a project.
    * Ability to execute project's branches, tags, labels, dashboards and so on:
        * Retrieves/Create/Delete
    * ...

* Ability to create/query Gerrit accounts, and ability to execute account:
    * Sets/Deletes the full name of an account.
    * Retrieves/Sets the status of an account.
    * Sets the username of an account.
    * Sets the display name of an account.
    * Checks if an account is active, and sets the account state to active/inactive.
    * Sets/Generates/Deletes the HTTP password of an account.
    * Retrieves a previously obtained OAuth access token.
    * Retrieves/Sets the user's (diff/edit) preferences.
    * Retrieves/Add/Deletes the watched projects of an account.
    * Retrieves/Delete the external ids of a user account.
    * Ability to execute account's emails, ssh keys, gpg keys.
        * Retrieves/Create/Delete
    * ...

* Ability to create/query Gerrit groups, and ability to execute group:
    * Renames a Gerrit internal group.
    * Sets/Deletes the description of a Gerrit internal group.
    * Sets the options of a Gerrit internal group.
    * Sets the owner group of a Gerrit internal group.
    * Gets the audit log of a Gerrit internal group.
    * Lists the direct members of a Gerrit internal group.
    * Retrieves/Adds/Removes a group member to a Gerrit internal group..
    * Lists/Retrieves/Adds/Removes the direct subgroups of a group.

* Ability to create/delete/query Gerrit changes, and ability to execute change:
    * Update/Abandon/Restore/Rebase/Move/Revert/Submit an existing change.
    * Creates a new patch set with a new commit message.
    * Retrieves/Sets/Deletes the topic of a change.
    * Retrieves/Sets/Deletes the assignee of a change.
    * Retrieves the branches and tags in which a change is included.
    * Lists the published comments, the robot comments of all revisions of the change.
    * Lists the draft comments of all revisions of the change that belong to the calling user.
    * Marks the change as (not) ready for review.
    * Marks the change to be private/non-private.
    * Marks/Un-marks a change as ignored.
    * Marks a change as reviewed/unreviewed.
    * Gets/Adds/Removes the hashtags associated with a change.
    * Ability to execute change's messages, change edit, reviewers, revision
    * Retrieves all users that are currently in the attention set, Adds a single user to the attention set of a change, Deletes a single user from the attention set of a change.
    * ...

* Ability to execute Gerrit config:
    * Retrieves/Sets the default user/diff/edit preferences for the server.
    * ...

* Ability to install/enable/disable/reload/query Gerrit plugins

Python versions
---------------

The project has been tested against Python versions:

* 3.6
* 3.7
* 3.8
* 3.9
* 3.10
* 3.11

Gerrit versions
---------------

Project tested on Version 3.8.0 Gerrit.

Important Links
---------------

Support and bug-reports: https://github.com/shijl0925/python-gerrit-api/issues?direction=desc&sort=comments&state=open

Project source code: github: https://github.com/shijl0925/python-gerrit-api

Project documentation: https://python-gerrit-api.readthedocs.org/en/latest/

Releases: http://pypi.python.org/pypi/python-gerrit-api

Donate
------

donations are not mandatory but very welcomed
If you like my work and want to support development or buy me a coffee `PayPal Donate <https://paypal.me/shijialiang0925>`_

Paypal
------
.. image:: https://raw.githubusercontent.com/andreostrovsky/donate-with-paypal/master/blue.svg
    :target: https://paypal.me/shijialiang0925

Wechat Pay
----------
.. image:: https://raw.githubusercontent.com/shijl0925/python-gerrit-api/master/docs/wechat.jpg

Alipay
------
.. image:: https://raw.githubusercontent.com/shijl0925/python-gerrit-api/master/docs/alipay.jpg
