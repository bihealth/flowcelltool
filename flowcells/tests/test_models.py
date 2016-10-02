# -*- coding: utf-8 -*-
"""Tests for the models from the flowcelltools Django app
"""

from test_plus.test import TestCase

from django.forms.models import model_to_dict

from .. import models


class TestSequencingMachine(TestCase):

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
