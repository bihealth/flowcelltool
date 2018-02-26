.. _install_on_flynn:

================
Install on Flynn
================

`Flynn <https://flynn.io/>`_ is a PaaS system similar to Heroku that you can run on your own hardware.

-------------
Prerequisites
-------------

Start by installing Flynn on your server and installing the ``flynn`` command line on your local machine as described in the `Flynn manual: Installation <https://flynn.io/docs/installation>`_.

--------------------
The Actual Deploying
--------------------

First, clone the repository from Github and get the latest stable version.

.. code-block:: shell

    $ git clone git@github.com:bihealth/flowcelltool.git
    $ git checkout v0.1.0

Then, create a new Flynn app

.. code-block:: shell

    $ cd flowcelltool
    $ flynn create flowcelltool
    Created flowcelltool

Next, provision a PostgreSQL database

.. code-block:: shell

    $ flynn resource add postgres
    Created resource d5d9350d-b55e-4102-a9d3-b5d4bbbd987c and release 56857385-d3ae-4c7e-8259-7fb2e184e064.

Create a Redis database for caching

.. code-block:: shell

    $ flynn resource add redis
    Created resource ba6187e7-1fed-4cb1-ae3f-d9f719d1ce69 and release 83e8b2da-9cc0-4c25-8668-a07c09493a55.

Ensure that the Flowcelltool Django app uses production settings.

.. code-block:: shell

    $ flynn env set DJANGO_SETTINGS_MODULE=config.settings.production

Set the Django key to something secret and set ``DJANGO_ALLOWED_HOSTS``.

.. code-block:: shell

    $ pwgen 100 1
    # ensure some random string is printed
    zaeFahB5oot3aiciegooheil0iSeis0ufahChaeveujumi3sai8sheequ6weewetushe7jei6veiBohhaiphoefelu0Eiy1nae3S
    $ flynn env set DJANGO_SECRET_KEY=$(pwgen 100 1)
    $ flynn env set DJANGO_ALLOWED_HOSTS='*'

Finally, deploy the application

.. code-block:: shell

    $ git push -u flynn master

Setup database using ``migrate``

.. code-block:: shell

    $ flynn run /app/manage.py migrate

Create a superuser

.. code-block:: shell

    $ flynn run /app/manage.py createsuperuser

Then follow the instructions of the ``createsuperuser`` command.

--------------------
Continuing From Here
--------------------

Now, continue with the :ref:`getting_started` guide or read on Email sending and LDAP authentication in :ref:`install_advanced`.
