===========
api/project
===========

Examples
--------

setup gerrit client and retrieve one project instance::

    from gerrit import GerritClient
    gerrit = GerritClient(base_url="https://yourgerrit", username='******', password='xxxxx')

    project = gerrit.projects.get('python-sonarqube-api')


Retrieves the description of a project.::

    description = project.description

Sets the description of a project.::

    input_ = {
        "description": "Plugin for Gerrit that handles the replication.",
        "commit_message": "Update the project description"
    }
    result = project.set_description(input_)

Deletes the description of a project.::

    project.delete_description()


Delete the project, requires delete-project plugin::

    project.delete()

Sets the configuration of a project.::

    input_ = {
        "description": "demo project",
        "use_contributor_agreements": "FALSE",
        "use_content_merge": "INHERIT",
        "use_signed_off_by": "INHERIT",
        "create_new_change_for_all_not_in_target": "INHERIT",
        "enable_signed_push": "INHERIT",
        "require_signed_push": "INHERIT",
        "reject_implicit_merges": "INHERIT",
        "require_change_id": "TRUE",
        "max_object_size_limit": "10m",
        "submit_type": "REBASE_IF_NECESSARY",
        "state": "ACTIVE"
    }
    result = project.set_config(input_)

Lists the access rights for a single project.::

    access_rights = project.access_rights

Create Change for review.::

    input_ = {
        "subject": "Let's support 100% Gerrit workflow direct in browser",
        "branch": "stable",
        "topic": "create-change-in-browser",
        "status": "NEW"
    }

    result = project.create_change(input_)


List the branches of a project. except the refs/meta/config::

    branches = project.branches

get a branch by ref::

    branch = project.branches.get('refs/heads/stable')

Creates a new branch.::

    input_ = {
        'revision': '76016386a0d8ecc7b6be212424978bb45959d668'
    }
    new_branch = project.branches.create('stable', input_)

Delete a branch.::

    project.branches.delete('refs/heads/stable')

Retrieves a commit of a project.::

    commit = project.get_commit('c641ab4dd180b4184f2663bd28277aa796b36417')

Retrieves the branches and tags in which a change is included.::

    result = commit.get_include_in()

Gets the content of a file from a certain commit.::

    content = commit.get_file_content('sonarqube/community/components.py')

Cherry-picks a commit of a project to a destination branch.::

    input_ = {
        "message": "Test Cherry Pick",
        "destination": "stable"
    }

    commit.cherry_pick(input_)

Lists the files that were modified, added or deleted in a commit.::

    result = commit.list_change_files()

