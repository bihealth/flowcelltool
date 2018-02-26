.. _import_barcodes:

===============
Manage Barcodes
===============

By default, the database of the web application is completely empty.
The first thing to add is a few barcodes.

The interface for managing barcode sets can be reached through the "Barcodes" link at the top and it is self-documenting.

Commonly used barcodes are available for download in the `Flowcelltool Github repository <https://github.com/bihealth/flowcelltool/tree/master/barcodes>`_.

.. note::

    Note that the barcode sequences should be given in **"forward" orientation**.
    Flowcelltool will automatically reverse-complement the second index in the case of dual indexing if the sequencing machine uses the `Illumina Dual-Index Paired-End Sequencing Workflow B <https://support.illumina.com/downloads/indexed-sequencing-overview-15057455.html>`_.

If you create your own barcode set then please share them by `creating a ticket in the Flowcelltool Github issue tracker <https://github.com/bihealth/flowcelltool>`_.
