.. _add_flowcells:

================
Manage Flowcells
================

The interface for managing flowcells can be reached through the "Flow Cells" link at the top.

The first step is first registering the flow cell with the necessary meta information.
The second step is then adding the library information.

Finally, you can export the flow cell sample sheet as:

- Illumina ``bcf2fastq`` 1.x sample sheet for older runs with RTA v1.x
- Illumina ``bcf2fastq`` 2.x sample sheet for older runs with RTA v2.x
- YAML-based sample sheets for use in `cubi_demux <https://github.com/bihealth/cubi_demux>`_.

-------------------
Creating Flow Cells
-------------------

You can create a new flow cell using the "Creat New" button on the Flow Cell management site.

Some details on the flow cell meta data fields:

Name
    The name of the flowcell, e.g., ``160303_ST-K12345_0815_A_BCDEFGHIXX_LABEL``.
    This follows the format convention ``${Date:YYMMDD}_${Machine_ID}_${Run_No}_${Slot}_${Flowcell_ID}[_${Label}]``.

Num Lanes
    The number of lanes on the flow cell, e.g., 8 for HiSeq, 4 for NextSeq.

Status
    The flow cell status:

    initial
        meta data record, sequencing not started

    sequencing complete
        sequencing is complete

    sequencing failed
        sequencing failed

    demultiplexing complete
        demultiplexing is complete

    demultiplexing started
        demultiplexing has started

    demultiplexing results delivered
        demultiplexing results (FASTQ) have been delivered as requested

    base calls delivered
        raw base calls have been delivered as requested

Sequencer Operator
    The operator on the sequencer (free text)

Demultiplexing Operator
    The operator for demultiplexing, must be a user in the Flowcelltool database

Index read Count
    Number of index adapters, ``0`` for no multiplexing, ``1`` for one adapter, ``2`` for two adapters.

RTA version
    The RTA version used (matching ``bcl2fastq`` version will be used)

Read length
    The length of the sequencing reads as configured.


----------------------------
Attaching Messages and Files
----------------------------

Once you have created a flowcell, you can add messages and attach files.
For example, this can be done for keeping a record of the sample sheets XLS files as received from the sequencing facility or attaching the QC report.

-------------------------
Copy-and-paste Excel Data
-------------------------

After creating a flow cell, you can add easily add data using copy and paste from Excel, using ``Actions`` -> ``Copy & Paste XLS``.
This will start a wizard that works as follows.

1. On the first wizard screen, copy and paste the sample information data from your sample sheet.
   This should contain at one column for each

    - the name of the sample
    - the name of the first barcode (as defined in the barcode set)
    - the column describing the lane (e.g., as ``1-4`` or ``1,2,4,5``)

   Optionally, you can also add the name of the second bacorde as well for dual indexing.

2. On the second screen, you can select the column for the sample, the column of the first barcode name, the first barcode set used (optionally also for the second barcode).
   Also, you should specify the number of the first data row and the column with the lanes that the library appears on.
   At the bottom, the pasted TSV data is previewed with column and row number.

3. Finally, the resulting data is previewed back to you for a last check and you can then store the libraries for the flow cell.

If you want to use the wizard with different barcode sets, you have to follow the process with each barcode set used.

Note that the barcode will be selected by the given name in the Excel sheet.
This will be done using a "longest matching suffix" rule, such that, e.g., for Agilent Agilent SureSelect V6 barcodes, the number "12" will be matched to "A12".
