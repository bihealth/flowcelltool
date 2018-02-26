===============
User Management
===============

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

-------------
Notes on LDAP
-------------

Note that when using LDAP, your users first have to log into the Flowcelltool system to get their account created in the Flowcelltool database.
You can then assign them into the appropriate roles.

When not using LDAP users, you can simply create users through the Django administration interface.
