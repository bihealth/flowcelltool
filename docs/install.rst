=====================
Installation Overview
=====================

Flowcelltool has been developed using the `The Twelve-Factor App <https://12factor.net/>`_ principles.
This means that deployment is easily possible on a wide range of platforms, including "classic" virtual machines as well as PAAS servers.

Here, the following installation options are documented:

:ref:`install_on_heroku`
    `Heroku <https://www.heroku.com>`_ is a platform as a service (PAAS) provider.
    Flowcelltool can be installed as a "free plan" application with a few clicks and without software to install on your local computer.

:ref:`install_on_flynn`
    `Flynn <https://www.flynn.io>`_ is an open source effort for easily providing self-hosted PAAS services, similar to Heroku.

:ref:`install_with_ansible`
    Install on a virtual machine.
    We document the necessary steps in an Ansible playbook.
    You can look at the Ansible playbook to figure out the steps for a manual installation.

:ref:`install_local`
    Create a local setup for the development of Flowcelltool.

After installation, refer to :ref:`getting_started` for information on getting the big picture.s
