Flowcell Tool
=============

Simple management of HTS Flowcells for demultiplexing

.. image:: https://img.shields.io/travis/bihealth/flowcelltool.svg
        :target: https://travis-ci.org/bihealth/flowcelltool

.. image:: https://readthedocs.org/projects/flowcelltool/badge/?version=latest
        :target: https://vcfpy.readthedocs.io/en/flowcelltool/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/bihealth/flowcelltool/shield.svg
        :target: https://pyup.io/repos/github/bihealth/flowcelltool/
        :alt: Updates

.. image:: https://api.codacy.com/project/badge/Grade/2272054a44fd41a6a8075f5d1bd44901
        :target: https://www.codacy.com/app/manuel-holtgrewe/flowcelltool?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bihealth/flowcelltool&amp;utm_campaign=Badge_Grade
        :alt: Codacy Analysis

.. image:: https://api.codacy.com/project/badge/Coverage/2272054a44fd41a6a8075f5d1bd44901
        :alt: Codacy Coverage
        :target: https://www.codacy.com/app/manuel-holtgrewe/vcfpy?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bihealth/flowcelltool&amp;utm_campaign=Badge_Coverage

.. image:: https://landscape.io/github/bihealth/flowcelltool/master/landscape.svg?style=flat
        :alt: Landscape Health
        :target: https://landscape.io/github/bihealth/flowcelltool

:License: MIT

:Status: ALPHA


Settings
--------

Moved to settings_.

.. _settings: http://cookiecutter-django.readthedocs.io/en/latest/settings.html

Basic Commands
--------------

Setting Up Your Users
^^^^^^^^^^^^^^^^^^^^^

* To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

* To create an **superuser account**, use this command::

    $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

Test coverage
^^^^^^^^^^^^^

To run the tests, check your test coverage, and generate an HTML coverage report::

    $ coverage run manage.py test
    $ coverage html
    $ open htmlcov/index.html

Running tests with py.test
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ py.test

Live reloading and Sass CSS compilation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Moved to `Live reloading and SASS compilation`_.

.. _`Live reloading and SASS compilation`: http://cookiecutter-django.readthedocs.io/en/latest/live-reloading-and-sass-compilation.html





Deployment
----------

The following details how to deploy this application.



Fixing Postgreqsl Encoding/UTF Errors
-------------------------------------

::

    sudo su postgres

    psql

    update pg_database set datistemplate=false where datname='template1';
    drop database Template1;
    create database template1 with owner=postgres encoding='UTF-8'

    lc_collate='en_US.utf8' lc_ctype='en_US.utf8' template template0;

    update pg_database set datistemplate=true where datname='template1';
