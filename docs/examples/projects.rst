Examples
--------

setup gerrit client::

    from gerrit import GerritClient
    gerrit = GerritClient(base_url="https://yourgerrit", username='******', password='xxxxx')

Lists the projects::

    projects = gerrit.projects.list()


Queries projects::

    projects = gerrit.projects.search(query="state:active")


Regex queries projects::

    projects = gerrit.projects.regex(query='test.*')


Retrieves a project.::

    project = gerrit.projects.get(project_name="MyProject1")


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

