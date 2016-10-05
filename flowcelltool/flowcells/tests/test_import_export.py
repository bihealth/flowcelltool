# -*- coding: utf-8 -*-
"""Tests for module import_export
"""

import textwrap

from test_plus.test import TestCase

from .. import import_export

from .test_models import BarcodeSetMixin, BarcodeSetEntryMixin


class TestBarcodeSetDumper(TestCase, BarcodeSetMixin, BarcodeSetEntryMixin):

    def setUp(self):
        self.barcode_set = self._make_barcode_set()
        self.barcode1 = self._make_barcode_set_entry(
            self.barcode_set, name='AR01', sequence='ATTA')
        self.barcode2 = self._make_barcode_set_entry(
            self.barcode_set, name='AR02', sequence='CGGC')

    def test_run(self):
        dumper = import_export.BarcodeSetDumper()
        RESULT = dumper.run(self.barcode_set)
        EXPECTED = textwrap.dedent(r"""
            {
              "name": "Agilent SureSelect XT Test",
              "short_name": "SureSelectTest",
              "description": null,
              "entries": [
                {
                  "name": "AR01",
                  "sequence": "ATTA"
                },
                {
                  "name": "AR02",
                  "sequence": "CGGC"
                }
              ]
            }
            """).lstrip()
        self.assertEqual(RESULT, EXPECTED)
