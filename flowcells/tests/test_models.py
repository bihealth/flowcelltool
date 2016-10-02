# -*- coding: utf-8 -*-
"""Tests for the models from the flowcelltools Django app
"""

from test_plus.test import TestCase

from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError

from .. import models


class TestSequencingMachine(TestCase):
    """Tests for models.SequencingMachine"""

    def setUp(self):
        self.machine = self._make_machine()

    def _make_machine(self):
        """Return SequencingMachine instance for testing"""
        values = {
            'vendor_id': 'NS5001234',
            'label': 'NextSeq#1',
            'description': 'In corner of lab 101',
            'machine_model': 'NextSeq',
            'slot_count': 1,
            'dual_index_workflow': 'A',
        }
        return models.SequencingMachine(**values)

    def test_initialization(self):
        EXPECTED = {
            'id': None,
            'vendor_id': 'NS5001234',
            'label': 'NextSeq#1',
            'description': 'In corner of lab 101',
            'machine_model': 'NextSeq',
            'slot_count': 1,
            'dual_index_workflow': 'A',
        }
        self.assertEqual(model_to_dict(self.machine), EXPECTED)

    def test__str__(self):
        EXPECTED = (
            "SequencingMachine('NS5001234', 'NextSeq#1', "
            "'In corner of lab 101', 'NextSeq', 1, 'A')")
        self.assertEqual(str(self.machine), EXPECTED)

    def test__repr__(self):
        EXPECTED = (
            "SequencingMachine('NS5001234', 'NextSeq#1', "
            "'In corner of lab 101', 'NextSeq', 1, 'A')")
        self.assertEqual(repr(self.machine), EXPECTED)


class BarcodeSetMixin:
    """Mixin for for _make_barcode_set()"""

    def _make_barcode_set(self):
        values = {
            'name': 'Agilent SureSelect XT',
            'short_name': 'SureSelect',
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
            'name': 'Agilent SureSelect XT',
            'short_name': 'SureSelect',
        }
        self.assertEqual(model_to_dict(self.barcode_set), EXPECTED)

    def test__str(self):
        EXPECTED = """Agilent SureSelect XT (SureSelect)"""
        self.assertEqual(str(self.barcode_set), EXPECTED)

    def test__repr__(self):
        EXPECTED = """BarcodeSet('Agilent SureSelect XT', 'SureSelect')"""
        self.assertEqual(repr(self.barcode_set), EXPECTED)


class TestBarcodeSetEntry(TestCase, BarcodeSetMixin):
    """Tests for models.BarcodeSetEntry"""

    def setUp(self):
        self.barcode_set = self._make_barcode_set()
        self.barcode = self._make_barcode_set_entry(self.barcode_set)

    def _make_barcode_set_entry(
            self, barcode_set, name='AR01', sequence='ACGTGTTA'):
        values = {
            'name': name,
            'sequence': sequence,
        }
        result = models.BarcodeSetEntry(barcode_set=barcode_set, **values)
        result.save()
        return result

    def test_initialization(self):
        EXPECTED = {
            'id': self.barcode.pk,
            'barcode_set': self.barcode_set.pk,
            'name': 'AR01',
            'sequence': 'ACGTGTTA',
        }
        self.assertEqual(model_to_dict(self.barcode), EXPECTED)

    def test__str(self):
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
