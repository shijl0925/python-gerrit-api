============
api/projects
============

Examples
--------

setup gerrit client::

    from gerrit import GerritClient
    client = GerritClient(base_url="https://yourgerrit", username='******', password='xxxxx')

Lists the projects::

    projects = client.projects.list()


Retrieves a project.::

    project = client.projects.get(project_name="MyProject")


Creates a new project.::

    input_ = {
        "description": "This is a demo project.",
        "submit_type": "INHERIT",
        "owners": [
          "MyProject-Owners"
        ]
    }
    project = client.projects.create('MyProject', input_)

Delete the project, requires delete-project plugin::

    client.projects.delete("MyProject")
    # or
    project = client.projects.get(project_name="MyProject")
    project.delete()
