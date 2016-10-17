===============
Getting Started
===============

.. warning::

   This is provisional information and needs some work.

Development Setup
-----------------

Create a super user (e.g., root)

.. code-block:: shell

    $ ./manage.py createsuperuser
    [follow the prompts]

Start server

.. code-block:: shell

    $ ./manage.py startserver

Now go to http://localhost:8080/admin, login and create a user for yourself.
Set the *super user* flag to the user to give him full permissions.

Then, go to http://localhost:8080/, logout, login as your user and go on with Import Barcodes guide.

Flynn Setup
-----------


Create a super user (e.g., root)

.. code-block:: shell

    $ flynn run /app/manage.py createsuperuser
    [follow the prompts]

Your server is already running, go to

Now go to https://flynnhost/admin, login and create a user for yourself.
Set the *super user* flag to the user to give him full permissions.
