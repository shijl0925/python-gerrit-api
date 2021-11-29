============
api/projects
============

Examples
--------

setup gerrit client::

    from gerrit import GerritClient
    gerrit = GerritClient(base_url="https://yourgerrit", username='******', password='xxxxx')

Lists the projects::

    projects = gerrit.projects.list()


Retrieves a project.::

    project = gerrit.projects.get(project_name="MyProject")


Creates a new project.::

    input_ = {
        "description": "This is a demo project.",
        "submit_type": "INHERIT",
        "owners": [
          "MyProject-Owners"
        ]
    }
    project = gerrit.projects.create('MyProject', input_)

Delete the project, requires delete-project plugin::

    gerrit.projects.delete("MyProject")
    # or
    project = gerrit.projects.get(project_name="MyProject")
    project.delete()
