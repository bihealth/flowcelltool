# -*- coding: utf-8 -*-
"""Tests for module import_export
"""

import textwrap

from test_plus.test import TestCase

from .. import import_export
from ..models import BarcodeSet, BarcodeSetEntry

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


class TestBarcodeSetLoader(TestCase):

    def test_run(self):
        # Check precondition
        self.assertEquals(BarcodeSet.objects.count(), 4)
        self.assertEquals(BarcodeSetEntry.objects.count(), 64)

        # Run barcode set loader
        loader = import_export.BarcodeSetLoader()
        JSON = textwrap.dedent(r"""
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
        barcode_set = loader.run(JSON)

        # Check resulting database state
        self.assertEquals(BarcodeSet.objects.count(), 5)
        self.assertEquals(BarcodeSetEntry.objects.count(), 66)
        self.assertEquals(barcode_set.name, 'Agilent SureSelect XT Test')
        self.assertEquals(barcode_set.short_name, 'SureSelectTest')
        self.assertEquals(barcode_set.entries.count(), 2)
        entries = list(barcode_set.entries.order_by('name'))
        self.assertEquals(entries[0].name, 'AR01')
        self.assertEquals(entries[0].sequence, 'ATTA')
        self.assertEquals(entries[1].name, 'AR02')
        self.assertEquals(entries[1].sequence, 'CGGC')
