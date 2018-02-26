.. _install_local:

=====================
Install Locally (Dev)
=====================

This section describes how to setup Flowcelltool in a virtualenv in a development environment.

-------------
Prerequisites
-------------

1. Install and configure Postgres.
2. Create a user and database for the application in the database.
   For example, ``flowcelltool_user`` with password ``flowcelltool_user`` and a database called ``flowcelltool``.
   Also, give the user the permission to create further Postgres databases (used for testing).

   You have to make the credentials in the environment variable ``DATABASE_URL``:

   .. code-block:: shell

       $ export DATABASE_URL='postgres://flowcelltool_user:flowcelltool_user@127.0.0.1/flowcelltool'

3. Install Python 3 (>= 3.4)

------------
Installation
------------

Next, clone the repository and setup the virtual environment inside

.. code-block:: shell

    $ git clone https://github.com/bihealth/flowcelltool.git
    $ virtualenv -p python3 .venv
    $ source .venv/bin/activate

Then, install the dependencies

.. code-block:: shell

    $ pip install --upgrade pip
    $ for f in requirements_*.txt; do pip install -r $f; done

Now, you can run the tests

.. code-block:: shell

    $ python manage.py test

Then, initialize the database:

.. code-block:: shell

    $ python manage.py migrate

Finally, start the server

.. code-block:: shell

    $ python manage.py runserver

--------------------
Continuing From Here
--------------------

Now, continue with the :ref:`getting_started` guide or read on Email sending and LDAP authentication in :ref:`install_advanced`.
