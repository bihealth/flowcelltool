============
Installation
============

.. warning::

   This is provisional information and needs some work.

Development Setup
=================

This section describes how to setup Flowcelltool in a virtualenv in a development environment.

First, create a postgresql users and a database for your application.
For example, ``flowcelltool_user`` with password ``flowcelltool_user`` and a database called ``flowcelltool``.
Also, give the user the permission to create further Postgres databases (used for testing).

You have to make the credentials in the environment variable ``DATABASE_URL``:

.. code-block:: shell

    $ export DATABASE_URL='postgres://flowcelltool_user:flowcelltool_user@127.0.0.1/flowcelltool'

Next, clone the repository and setup the virtual environment inside

.. code-block:: shell

    $ git clone git@github.com:bihealth/flowcelltool.git
    $ virtualenv -p python3 .venv
    $ source .venv/bin/activate

Then, install the dependencies

.. code-block:: shell

    $ pip install --upgrade pip
    $ for f in requirements/*.txt; do pip install -r $f; done

Now, you can run the tests

.. code-block:: shell

    $ ./manage.py test

Finally, initialize the database:

.. code-block:: shell

    $ ./manage.py migrate

From here on, you can follow the Getting Started guide.

LDAP/ActiveDirectory Setup
==========================

You can setup the tool to use LDAP/ActiveDirectory for logging into your web app.
For this, set the following environment variables:

.. code-block:: shell

    export AUTH_LDAP_BIND_DN='CN=user,DC=example,DC=com'
    export AUTH_LDAP_BIND_PASSWORD='password'
    export AUTH_LDAP_SERVER_URI='ldap://activedirectory.example.com'
    export AUTH_LDAP_USER_SEARCH_BASE='DC=example,DC=com'
