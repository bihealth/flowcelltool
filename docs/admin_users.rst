======================
Admin: User Management
======================

.. warning::

   This is provisional information and needs some work.

User management works through the Django admin interface which lives at ``/admin`` of your application.
Super users also have a link to "Site Admin" in the top bar.

The following settings affect the permissions of a user:

- **is superuser** flag, users can do everything
- groups
    - **Instrument Operator** -- create flow cell, update flow cell created by the same user
    - **Demultiplexing Operator** -- create flow cell, update any flow cell
    - **Demultiplexing Admin** -- all of above, also CRUD of barcode set and instrument records
    - **Import Bot** - create new flow cells, for future use
