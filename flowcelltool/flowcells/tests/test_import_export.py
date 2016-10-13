# -*- coding: utf-8 -*-
"""Tests for module import_export
"""

import textwrap

from test_plus.test import TestCase

from .. import import_export
from ..models import BarcodeSet, BarcodeSetEntry
from .. import models

from .test_models import SequencingMachineMixin, FlowCellMixin, \
    BarcodeSetMixin, BarcodeSetEntryMixin, LibraryMixin


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
        self.assertEquals(BarcodeSet.objects.count(), 0)
        self.assertEquals(BarcodeSetEntry.objects.count(), 0)

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
        self.assertEquals(BarcodeSet.objects.count(), 1)
        self.assertEquals(BarcodeSetEntry.objects.count(), 2)
        self.assertEquals(barcode_set.name, 'Agilent SureSelect XT Test')
        self.assertEquals(barcode_set.short_name, 'SureSelectTest')
        self.assertEquals(barcode_set.entries.count(), 2)
        entries = list(barcode_set.entries.order_by('name'))
        self.assertEquals(entries[0].name, 'AR01')
        self.assertEquals(entries[0].sequence, 'ATTA')
        self.assertEquals(entries[1].name, 'AR02')
        self.assertEquals(entries[1].sequence, 'CGGC')


class Library(TestCase, LibraryMixin, SequencingMachineMixin, FlowCellMixin,
              BarcodeSetEntryMixin, BarcodeSetMixin):

    def setUp(self):
        self.user = self.make_user()
        self.machine = self._make_machine()
        self.barcode_set = self._make_barcode_set()
        self.barcode = self._make_barcode_set_entry(self.barcode_set)
        self.barcode2 = self._make_barcode_set_entry(
            self.barcode_set, 'AR02', 'CGATATA')
        self.flow_cell_name = '160303_{}_0815_A_BCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.flow_cell = self._make_flow_cell(
            self.user, self.flow_cell_name, 8,
            models.FLOWCELL_STATUS_SEQ_COMPLETE, 'John Doe',
            True, 1, models.RTA_VERSION_V2, 151, 'Description')
        self.library = self._make_library(
            self.flow_cell, 'LIB_001', models.REFERENCE_HUMAN,
            self.barcode_set, self.barcode, [1, 2],
            self.barcode_set, self.barcode2)
        self.generator = import_export.FlowCellSampleSheetGenerator(
            self.flow_cell)

    def test_build_yaml(self):
        RESULT = self.generator.build_yaml()
        self.maxDiff = None
        EXPECTED = textwrap.dedent(r"""
            # CUBI Flow Cell YAML
            - name: '160303_NS5001234_0815_A_BCDEFGHIXX_LABEL'
              num_lanes: 8
              operator: 'John Doe'
              rta_version: 2
              is_paired: true
              status: seq_complete
              read_length: 151
              libraries:
                - name: 'LIB_001'
                  reference: 'hg19'
                  barcode_set: 'SureSelectTest'
                  barcode:
                    name: 'AR01'
                    seq: 'ACGTGTTA'
                  lanes: [1, 2]
        """).lstrip()
        self.assertEqual(RESULT, EXPECTED)

    def test_build_v1(self):
        RESULT = self.generator.build_v1()
        EXPECTED = textwrap.dedent(r"""
            FCID,Lane,SampleID,SampleRef,Index,Description,Control,Recipe,Operator,SampleProject
            BCDEFGHIXX,1,LIB_001,hg19,ACGTGTTA,,N,PE_indexing,John Doe,Project
            BCDEFGHIXX,2,LIB_001,hg19,ACGTGTTA,,N,PE_indexing,John Doe,Project
        """).lstrip()
        self.assertEqual(RESULT, EXPECTED)

    def test_build_v2(self):
        RESULT = self.generator.build_v2()
        EXPECTED = textwrap.dedent(r"""
            [Header]
            IEMFileVersion,4
            Investigator Name,John Doe
            Experiment Name,Project
            Date,16/03/03
            Workflow,GenerateFASTQ
            Applications,FASTQ Only
            Assay,TruSeq HT
            Description,

            [Reads]
            151
            151

            [Data]
            Lane,Sample_ID,Sample_Name,Sample_Plate,Sample_Well,i7_Index_ID,index,Sample_Project,Description
            1,LIB_001,,,,AR01,ACGTGTTA,Project,
            2,LIB_001,,,,AR01,ACGTGTTA,Project,
        """).lstrip()
        self.assertEqual(RESULT, EXPECTED)
