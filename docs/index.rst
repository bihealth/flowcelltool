Welcome to Flowcelltool's documentation!
=========================================

Flowcelltool is a Django web application for the management of Illumina flow cells.
The documentation is split into three parts (accessible through the navigation on the left):

Installation & Getting Started
    Instructions for the installation of the web application and its deployment

Manual
    This section contains the user documentation

Project Info
    More information on the project, including the changelog, list of contributing authors, and contribution instructions.

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

`The Project repository can be found on Github.com <https://github.com/bihealth/flowcelltool>`_.

.. toctree::
    :caption: Installation & Getting Started
    :name: getting-started
    :hidden:
    :maxdepth: 1

    install
    install_heroku
    install_flynn
    install_ansible
    install_local
    install_advanced

.. toctree::
    :caption: User Manual
    :name: user-manual
    :hidden:
    :maxdepth: 1
    :titlesonly:

    getting_started
    manage_barcodes
    manage_sequencers
    manage_flowcells
    manage_users

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
