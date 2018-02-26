.. _install_advanced:

===========================
Configure Advanced Features
===========================

This section describes how to configure some advanced features:

- LDAP authentication
- Sending of emails

.. _configure_outgoing_email:

----------------------------
Outgoing Email Configuration
----------------------------

You have to set the SMTP server for outgoing mail using the environment variable ``EMAIL_URL``

On Heroku
=========

Simply configure ``EMAIL_URL`` "Config Variable" in the Heroku application configuration.

::

    EMAIL_URL=smtp://post-office.example.com

On Flynn
========

.. code-block:: shell

    $ flynn env set EMAIL_URL=smtp://post-office.example.com

On Manual / Ansible Deployment
==============================

You have to set the variable similar to ``DATABASE_URL`` in ``/etc/systemd/system/flowcelltool.service``.
When using Ansible, you best configure this in ``templates/flowcelltool.service.j2``.

::

    Environment="EMAIL_URL=smtp://post-office.example.com"

------------------
LDAP Configuration
------------------

Flowcelltool can use up to two LDAP servers (ActiveDirectory is also supported) for authentication users.
The configuration of the second one is optional.
For one server, you can either configure the server to user ``username`` for login or ``username@DOMAIN`` with a configurable domain.

To enable this for the first server, define the following environment variables (see :ref:`configure_outgoing_email` on the appropriate places for the different deployment targets).

The configuration of ``AUTH_LDAP_USERNAME_DOMAIN`` is optional when only using one server.

.. code-block:: shell

    ENABLE_LDAP=1
    AUTH_LDAP_BIND_DN='CN=user,DC=example,DC=com'
    AUTH_LDAP_BIND_PASSWORD='password'
    AUTH_LDAP_SERVER_URI='ldap://activedirectory.example.com'
    AUTH_LDAP_USER_SEARCH_BASE='DC=example,DC=com'
    AUTH_LDAP_USERNAME_DOMAIN='YOURDOMAIN'

For configuring the secondary LDAP server, use the following environment variables.
The configuration of ``AUTH_LDAP_USERNAME_DOMAIN`` is **required** when using two servers.

.. code-block:: shell

    export ENABLE_LDAP_SECONDARY=1
    export AUTH_LDAP2_BIND_DN='CN=user,DC=example,DC=com'
    export AUTH_LDAP2_BIND_PASSWORD='password'
    export AUTH_LDAP2_SERVER_URI='ldap://activedirectory.example.com'
    export AUTH_LDAP2_USER_SEARCH_BASE='DC=example,DC=com'
    export AUTH_LDAP2_USERNAME_DOMAIN='YOURDOMAIN2'

Note that for users logging in via LDAP, the username must be in form of ``username@YOURDOMAIN`` if the ``AUTH_LDAP*_USERNAME_DOMAIN`` variable is set.

.. note::

    If you alter the username domain configuration once the tool is in use, you must manually alter the user names already found in the Django Postgres database.
