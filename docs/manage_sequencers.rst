.. _create_sequencers:

=================
Manage Sequencers
=================

Also, there are no sequencing machines added by default.

The interface for managing sequencers can be reached through the "Sequencers" link at the top and it is self-documenting.

Some notes on the sequencer fields:

Vendor ID
    The ID of the device, e.g., ``ST-K00100`` or ``NB501000``.

Label
    A short name of the device, e.g., "HiSeq 4000 in Lab 101"

Machine Model
    The machine model.

Slot count
    Number of slots in the device (e.g., ``1`` for NextSeq 500 and and ``2`` for HiSeq 4000).

Dual index workflow
    The dual indexing workflow as described in the `Illumina Indexed Sequencing Overview Guide <https://support.illumina.com/downloads/indexed-sequencing-overview-15057455.html>`_

The ``Vendor ID`` is also encoded in the flowcell run output directory name.
This information will be used for automatically reverse-complementing the second index on dual indexing based on the device used for sequencing a flowcell.
