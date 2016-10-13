# -*- coding: utf-8 -*-
"""Tests for the models from the flowcelltools Django app
"""

from test_plus.test import TestCase

from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError

from .. import models


class SequencingMachineMixin:
    """Helper mixin class to provide _make_machine"""

    def _make_machine(self):
        """Return SequencingMachine instance for testing"""
        values = {
            'vendor_id': 'NS5001234',
            'label': 'NextSeq#1',
            'description': 'In corner of lab 101',
            'machine_model': models.MACHINE_MODEL_NEXTSEQ500,
            'slot_count': 1,
            'dual_index_workflow': models.INDEX_WORKFLOW_A,
        }
        result = models.SequencingMachine(**values)
        result.save()
        return result


class TestSequencingMachine(TestCase, SequencingMachineMixin):
    """Tests for models.SequencingMachine"""

    def setUp(self):
        self.machine = self._make_machine()

    def test_initialization(self):
        EXPECTED = {
            'id': self.machine.pk,
            'vendor_id': 'NS5001234',
            'label': 'NextSeq#1',
            'description': 'In corner of lab 101',
            'machine_model': models.MACHINE_MODEL_NEXTSEQ500,
            'slot_count': 1,
            'dual_index_workflow': models.INDEX_WORKFLOW_A,
        }
        self.assertEqual(model_to_dict(self.machine), EXPECTED)

    def test__str__(self):
        EXPECTED = (
            "SequencingMachine('NS5001234', 'NextSeq#1', "
            "'In corner of lab 101', 'NextSeq500', 1, 'A')")
        self.assertEqual(str(self.machine), EXPECTED)

    def test__repr__(self):
        EXPECTED = (
            "SequencingMachine('NS5001234', 'NextSeq#1', "
            "'In corner of lab 101', 'NextSeq500', 1, 'A')")
        self.assertEqual(repr(self.machine), EXPECTED)


class BarcodeSetMixin:
    """Mixin for for _make_barcode_set()"""

    def _make_barcode_set(self):
        values = {
            'name': 'Agilent SureSelect XT Test',
            'short_name': 'SureSelectTest',
        }
        result = models.BarcodeSet(**values)
        result.save()
        return result


class TestBarcodeSet(TestCase, BarcodeSetMixin):
    """Tests for models.BarcodeSet"""

    def setUp(self):
        self.barcode_set = self._make_barcode_set()

    def test_initialization(self):
        EXPECTED = {
            'id': self.barcode_set.pk,
            'description': None,
            'name': 'Agilent SureSelect XT Test',
            'short_name': 'SureSelectTest',
        }
        self.assertEqual(model_to_dict(self.barcode_set), EXPECTED)

    def test__str(self):
        EXPECTED = """Agilent SureSelect XT Test (SureSelectTest)"""
        self.assertEqual(str(self.barcode_set), EXPECTED)

    def test__repr__(self):
        EXPECTED = (
            """BarcodeSet('Agilent SureSelect XT Test', """
            """'SureSelectTest')""")
        self.assertEqual(repr(self.barcode_set), EXPECTED)


class BarcodeSetEntryMixin:
    """Mixin for for _make_barcode_set()"""

    def _make_barcode_set_entry(
            self, barcode_set, name='AR01', sequence='ACGTGTTA'):
        values = {
            'name': name,
            'sequence': sequence,
            'barcode_set': barcode_set,
        }
        result = models.BarcodeSetEntry(**values)
        result.save()
        return result


class TestBarcodeSetEntry(TestCase, BarcodeSetEntryMixin, BarcodeSetMixin):
    """Tests for models.BarcodeSetEntry"""

    def setUp(self):
        self.barcode_set = self._make_barcode_set()
        self.barcode = self._make_barcode_set_entry(self.barcode_set)

    def test_initialization(self):
        EXPECTED = {
            'id': self.barcode.pk,
            'barcode_set': self.barcode_set.pk,
            'name': 'AR01',
            'sequence': 'ACGTGTTA',
        }
        self.assertEqual(model_to_dict(self.barcode), EXPECTED)

    def test__str__(self):
        EXPECTED = """AR01 (ACGTGTTA)"""
        self.assertEqual(str(self.barcode), EXPECTED)

    def test__repr__(self):
        EXPECTED = """BarcodeSetEntry('AR01', 'ACGTGTTA')"""
        self.assertEqual(repr(self.barcode), EXPECTED)

    def test_unique_name(self):
        """Check uniqueness of the name is enforced"""
        with self.assertRaises(ValidationError):
            self._make_barcode_set_entry(self.barcode_set, 'AR01', 'NNNNNNNN')

    def test_unique_sequence(self):
        """Check uniqueness of the sequence is enforced"""
        with self.assertRaises(ValidationError):
            self._make_barcode_set_entry(self.barcode_set, 'ARNN', 'ACGTGTTA')


class FlowCellMixin:
    """Helper mixin that provides _make_flow_cell()"""

    def _make_flow_cell(
            self, owner, name, num_lanes, status, operator, is_paired,
            index_read_count, rta_version, read_length, description):
        values = {
            'owner': owner,
            'name': name,
            'num_lanes': num_lanes,
            'status': status,
            'operator': operator,
            'is_paired': is_paired,
            'index_read_count': index_read_count,
            'rta_version': rta_version,
            'read_length': read_length,
            'description': description
        }
        result = models.FlowCell(**values)
        result.save()
        return result


class TestFlowCell(TestCase, SequencingMachineMixin, FlowCellMixin,
                   BarcodeSetEntryMixin, BarcodeSetMixin):

    def setUp(self):
        self.user = self.make_user()
        self.machine = self._make_machine()
        self.barcode_set = self._make_barcode_set()
        self.barcode = self._make_barcode_set_entry(self.barcode_set)
        self.flow_cell_name = '160303_{}_0815_A_BCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.flow_cell = self._make_flow_cell(
            self.user, self.flow_cell_name, 8,
            models.FLOWCELL_STATUS_SEQ_COMPLETE, 'John Doe',
            True, 1, models.RTA_VERSION_V2, 151, 'Description')

    def test_initialization(self):
        EXPECTED = {
            'id': self.flow_cell.pk,
            'owner': self.user.pk,
            'name': self.flow_cell_name,
            'description': 'Description',
            'sequencing_machine': self.machine.pk,
            'num_lanes': 8,
            'status': models.FLOWCELL_STATUS_SEQ_COMPLETE,
            'operator': 'John Doe',
            'is_paired': True,
            'index_read_count': 1,
            'rta_version': models.RTA_VERSION_V2,
            'read_length': 151,
        }
        self.assertEqual(model_to_dict(self.flow_cell), EXPECTED)

    def test__str__(self):
        EXPECTED = '160303_NS5001234_0815_A_BCDEFGHIXX_LABEL'
        self.assertEqual(str(self.flow_cell), EXPECTED)

    def test__repr__(self):
        EXPECTED = (
            r"""FlowCell('160303_NS5001234_0815_A_BCDEFGHIXX_LABEL', """
            r"""SequencingMachine('NS5001234', 'NextSeq#1', 'In corner of """
            r"""lab 101', 'NextSeq500', 1, 'A'), 8, 'seq_complete', """
            r"""'John Doe', True, 1, 2, 151)""")
        self.assertEqual(repr(self.flow_cell), EXPECTED)

    def test_validate_sequencer(self):
        self._make_flow_cell(
            self.user, self.flow_cell_name, 8,
            models.FLOWCELL_STATUS_SEQ_COMPLETE, 'John Doe',
            True, 1, models.RTA_VERSION_V2, 151, 'Description')

    def test_tokens(self):
        self.assertEquals(self.flow_cell.token_date(), '160303')
        self.assertEquals(self.flow_cell.token_instrument(), 'NS5001234')
        self.assertEquals(self.flow_cell.token_run_no(), '0815')
        self.assertEquals(self.flow_cell.token_slot(), 'A')
        self.assertEquals(self.flow_cell.token_vendor_id(), 'BCDEFGHIXX')
        self.assertEquals(self.flow_cell.token_label(), 'LABEL')


class LibraryMixin:
    """Helper mixin that provides _make_library()"""

    def _make_library(
            self, flow_cell, name, reference, barcode_set, barcode,
            lane_numbers, barcode_set2=None, barcode2=None):
        values = {
            'flow_cell': flow_cell,
            'name': name,
            'reference': reference,
            'barcode_set': barcode_set,
            'barcode': barcode,
            'lane_numbers': lane_numbers,
            'barcode_set2': barcode_set2,
            'barcode2': barcode2,
        }
        result = models.Library(**values)
        result.save()
        return result


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

    def test_initialization(self):
        EXPECTED = {
            'id': self.library.pk,
            'barcode': self.barcode.pk,
            'barcode_set': self.barcode_set.pk,
            'barcode2': self.barcode2.pk,
            'barcode_set2': self.barcode_set.pk,
            'flow_cell': self.flow_cell.pk,
            'lane_numbers': [1, 2],
            'name': 'LIB_001',
            'reference': models.REFERENCE_HUMAN
        }
        self.assertEqual(model_to_dict(self.library), EXPECTED)

    def test__str__(self):
        EXPECTED = 'LIB_001 (AR01:ACGTGTTA, AR02:CGATATA)'
        self.assertEqual(str(self.library), EXPECTED)

    def test__repr__(self):
        EXPECTED = (
            r"""Library('160303_NS5001234_0815_A_BCDEFGHIXX_LABEL', """
            r"""'hg19', BarcodeSet('Agilent SureSelect XT Test', """
            r"""'SureSelectTest'), """
            r"""BarcodeSetEntry('AR01', 'ACGTGTTA'), [1, 2])""")
        self.assertEqual(repr(self.library), EXPECTED)

    def test_validate_uniqueness_violate_name(self):
        with self.assertRaises(ValidationError):
            self._make_library(
                self.flow_cell, 'LIB_001', models.REFERENCE_HUMAN,
                self.barcode_set, self.barcode2, [2])

    def test_validate_uniqueness_violate_barcode(self):
        with self.assertRaises(ValidationError):
            self._make_library(
                self.flow_cell, 'LIB_002', models.REFERENCE_HUMAN,
                self.barcode_set, self.barcode, [2])

    def test_validate_uniqueness_violate_barcode2(self):
        with self.assertRaises(ValidationError):
            self._make_library(
                self.flow_cell, 'LIB_002', models.REFERENCE_HUMAN,
                self.barcode_set, self.barcode2, [2],
                self.barcode_set, self.barcode2)

    def test_validate_lane_nos(self):
        with self.assertRaises(ValidationError):
            self._make_library(
                self.flow_cell, 'LIB_002', models.REFERENCE_HUMAN,
                self.barcode_set, self.barcode, [9, 10])

    def test_validate_flow_cell_lane_nos_(self):
        """Check that the lane count is compatible with lane numbers in the
        contained libraries
        """
        library2 = self._make_library(
            self.flow_cell, 'LIB_001', models.REFERENCE_HUMAN,
            self.barcode_set, self.barcode2, [8])
        self.flow_cell.num_lanes = 4
        with self.assertRaises(ValidationError):
            self.flow_cell.save()
