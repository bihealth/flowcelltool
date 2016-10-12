Welcome to Flowcelltool's documentation!
=========================================

.. warning::

   Flowcelltool is currently not stable and under active development.
   Things will change and break, at least until the first v0.1 release.

Flowcelltool is a Django web application for the management of Illumina flow cells.
The documentation is split into three parts (accessible through the navigation on the left):

Installation & Getting Started
    Instructions for the installation of the web application and its deployment

Manual
    This section contains the user documentation

Project Info
    More information on the project, including the changelog, list of contributing authors, and contribution instructions.

Screenshot
----------

* TODO

Dependencies
------------

* Python 3
* Django 1.10
* PostgreSQL

Features
--------

* Graphical management of flow cells and libraries
* Automated generation of bcl2fastq (both v1.x and v2.x) sample sheets
* Authentication via LDAP/ActiveDirectory or local users
* Easily deployable to Heroku/Flynn.io/Docker (12 factor app), follows Two Scoops of Python best pratice

.. toctree::
    :caption: Installation & Getting Started
    :name: getting-started
    :hidden:
    :maxdepth: 1

    installation
    getting_started

.. toctree::
    :caption: User Manual
    :name: user-manual
    :hidden:
    :maxdepth: 1
    :titlesonly:

    import_barcodes
    create_sequencers
    add_flowcells
    admin_users

.. toctree::
    :caption: Project Info
    :name: project-info
    :hidden:
    :maxdepth: 1
    :titlesonly:

    contributing
    authors
    history
    license

.. Generated pages, should not appear

    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`
