=======
History
=======

----
HEAD
----

- Differentiating between "initial state" and "ready" for demultiplexing.
- Allow flagging individual steps as ``complete_warnings``.
- Fixing issue with validation errors late in the XLSX import (#141, #142).
- Adding ``manual_label`` to ``FlowCell`` (#147).
- Adding run number to flowcell list.
- Fixing flow cell order.
- Fixing bug in flow cell list.
- Changing API ``flowcell/by_vendor_id`` to ``flowcell_resolve``.

------
v0.3.0
------

- Adding UI for fast status updates.
- Refactoring concept of flowcell state, splitting into sequencing/conversion/delivery.
- Major refactoring of the UI and data models for automatization.
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
