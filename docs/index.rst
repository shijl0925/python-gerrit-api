.. Gerrit Client with Python documentation master file, created by
   sphinx-quickstart on Fri Oct 16 16:34:37 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Gerrit Client with Python's documentation!
=====================================================

python-gerrit-api provides a simple interface for clients to interact with Gerrit via the REST API.

Compatibility
=============

* This package is compatible Python versions 2.7, 3.5+.


Installation
============

Use :command:`pip` to install the latest stable version of ``python-gerrit-api``:

.. code-block:: console

   $ sudo pip install python-gerrit-api

The current development version is available on `github
<https://github.com/shijl0925/python-gerrit-api>`__. Use :command:`git` and
:command:`python setup.py` to install it:

.. code-block:: console

   $ git clone https://github.com/shijl0925/python-gerrit-api.git
   $ cd python-gerrit-api
   $ sudo python setup.py install



Change Log
==========

See the `CHANGELOG.md <https://github.com/shijl0925/python-gerrit-api/blob/master/CHANGELOG.md>`_ file.


Documentation
=============

This part of the documentation will show you how to get started in using python-gerrit-api.

The Client is easy to use, you just need to initialize it with the connection parameters.

Setup a Gerrit Client
------------------------
.. code-block:: python

    from gerrit import GerritClient

    client = GerritClient(base_url="https://yourgerrit", username='******', password='xxxxx')


Example
-------
Refer to the example script for a full working example.

.. toctree::
   :maxdepth: 2

   examples

API Reference
-------------

If you are looking for information on a specific function, class or
method, this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   gerrit
   gerrit.accounts
   gerrit.changes
   gerrit.groups
   gerrit.projects
   gerrit.config
   gerrit.gitiles
   gerrit.plugins

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
