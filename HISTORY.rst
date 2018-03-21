=======
History
=======

----
HEAD
----

- Refactoring API and adding tests for it.
  Note that the API is still unstable (shown by having version ``v0``), it will become properly versioned from ``v1`` on.

------
v0.2.0
------

- Switching to UUID for all public-facing IDs.
- Adding support for message and multi-attachment upload via API.
- Adding basic profile page.
- Switching layout and vendoring JS/CSS dependencies.
- Adding adapter and quality JSON fields to ``FlowCell`` and APIs to set them.
- Some layout / UI refinements.
- Adding unstable API, mostly read-only except for what is needed for automated demultiplexing and QC.
- Adding UI for generating REST API login tokens.
- Allowing to specify message on login screen via environment variable.
- Adding version to stick footer.

------
v0.1.1
------

- Fixing display of libraries.

------
v0.1.0
------

- Initial release. Everything is new.
