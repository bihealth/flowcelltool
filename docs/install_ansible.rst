.. _install_with_ansible:

=====================
Install using Ansible
=====================

`Ansible <https://www.ansible.com>`_ is a software for the management of servers and can be used for automatically deploying Flowceltool.

You can also easily infer the steps for manual deployment from the Ansible playbook.

-------------
Prerequisites
-------------

1. You have setup a virtual machine with CentOS 7.4 Linux.
   (Of course, any modern Linux will work but will need adjustments to the Ansible playbook file).
2. You can connect to the VM as user root with ``SSH`` (i.e., you properly setup the ``authorized_keys`` for root and configured the SSH server appropriately).
3. You have Ansible (>=2.4) installed on your local machine (e.g., using ``pip install ansible``).
4. You have the ``pwgen`` binary installed on your local machine.

------------
Installation
------------

First, clone the repository from Github and get the latest stable version.

.. code-block:: shell

    $ git clone git@github.com:bihealth/flowcelltool.git
    $ git checkout v0.1.0

Create an ``inventory`` file in the ``ansible`` sub directory with the remote server's hostname.

Note that we use Ansible variables here to set the name and password of the Postgres user that Flowcelltool will use.
Also note that you can change the Flowcelltool version here and the automatically created super user name (default: ``root``) and password (default: ``"password"``).
In a more refined Ansible setup, you would use vault-encrypted host variables.

.. code-block:: shell

    $ cat <<EOF >inventories.yml
    ---
    flowcelltool-servers:
        hosts:
            "your-vm-hostname":
                # Postgres Configuration
                #
                # Postgres database to create
                FLOWCELLTOOL_DB: 'flowcelltool'
                # User to use for connecting to postgres server
                FLOWCELLTOOL_PG_USER: 'flowcelltool'
                # Password of user defined above
                FLOWCELLTOOL_PG_PASSWORD: 'flowcellpass'

                # Flowcelltool Configuration
                #
                # Version of Flowcelltool to install
                FLOWCELLTOOL_VERSION: 'stable'
                # Super user name to create
                FLOWCELLTOOL_SUPERUSER: root
                # Super user password to set
                FLOWCELLTOOL_SUPERUSER_PW: password
                # Generate secret key
                DJANGO_SECRET_KEY: '`pwgen -N 1 40`'
    EOF

Now, execute the Ansible playbook.

.. code-block:: shell

    $ ansible-playbook -i inventory.yml inst-flowcelltool-centos.yml

Ansible playbooks are easy to read!
If you want to find out how to install Flowcelltool manually.

Note that this will setup a PostgreSQL databse, Nginx as a reverse proxy, and the Flowcell app itself.
However, also note that it will only perform a setup for HTTP on port 80 and not yet an HTTPS server.

You can then go to ``https://your-vm-hostname`` and login with the user and password configured above.
Of course, you will have to confirm the security exception for the self-signed SSL certificate.

--------------------
Continuing From Here
--------------------

Now, continue with the :ref:`getting_started` guide or read on Email sending and LDAP authentication in :ref:`install_advanced`.
