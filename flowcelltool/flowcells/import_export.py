# -*- coding: utf-8 -*-
"""Code for importing and exporting database records to YAML/JSON"""

from collections import OrderedDict
import json

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


class BarcodeSetDumper:
    """Helper class for dumping BarcodeSet objects to JSON

    They can be imported later with BarcodeSetLoader again.
    """

    @classmethod
    def run(klass, barcode_set):
        """Return JSON dump of BarcodeSet in barcode_set as string"""
        # Get base fields
        result = OrderedDict()
        for fname in ('name', 'short_name', 'description'):
            result[fname] = getattr(barcode_set, fname)
        # Get barcode set entries
        result['entries'] = []
        for entry in barcode_set.entries.order_by('name'):
            result['entries'].append(OrderedDict(
                [
                    ('name', entry.name),
                    ('sequence', entry.sequence),
                ]))
        return json.dumps(result, indent=2) + '\n'
