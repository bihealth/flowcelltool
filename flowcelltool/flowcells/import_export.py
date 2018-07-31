# -*- coding: utf-8 -*-
"""Code for importing and exporting database records to CSV and YAML sample sheets"""

from collections import OrderedDict
import datetime
import json

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import (
    BarcodeSet, FlowCell, SequencingMachine, INDEX_WORKFLOW_A)

# TODO: rename appropriately, we are using DRF serializer's for JSON now


__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


def revcomp(s):
    """Reverse complement function"""
    comp_map = {
        'A': 'T',
        'a': 't',
        'C': 'G',
        'c': 'g',
        'g': 'c',
        'G': 'C',
        'T': 'A',
        't': 'a',
    }
    return ''.join(reversed([comp_map.get(x, x) for x in s]))


def identity(s):
    """Identity function"""
    return s


class FlowCellSampleSheetGenerator:
    """Helper class for generating sample sheet from FlowCell instance"""

    def __init__(self, flow_cell):
        #: The flow cell to dump
        self.flow_cell = flow_cell

    def build_yaml(self):
        """Return YAML representation of sample sheet"""
        if (self.flow_cell.sequencing_machine.dual_index_workflow ==
                INDEX_WORKFLOW_A):
            idx2mod = identity
        else:
            idx2mod = revcomp
        rows = [
            '# CUBI Flow Cell YAML',
            '- name: {}'.format(repr(self.flow_cell.get_full_name())),
            '  num_lanes: {}'.format(self.flow_cell.num_lanes),
            '  operator: {}'.format(repr(self.flow_cell.operator)),
            '  rta_version: {}'.format(self.flow_cell.rta_version),
            '  is_paired: {}'.format(
                'true' if self.flow_cell.is_paired else 'false'),
            '  status_sequencing: {}'.format(self.flow_cell.status_delivery),
            '  status_conversion: {}'.format(self.flow_cell.status_conversion),
            '  status_delivery: {}'.format(self.flow_cell.status_delivery),
            '  delivery_type: {}'.format(self.flow_cell.delivery_type),
            '  read_length: {}'.format(self.flow_cell.read_length),
            '  bcl2fastq_args:',
            '    barcode_mismatches: {}'.format(
                'null' if self.flow_cell.barcode_mismatches is None
                else self.flow_cell.barcode_mismatches),
        ]
        if not self.flow_cell.libraries.count():
            rows.append('  libraries: []')
            return '\n'.join(rows)
        rows.append('  libraries:')
        for lib in self.flow_cell.libraries.order_by('name'):
            if lib.barcode_set.set_type == '10x_genomics':
                seqs = [
                    ('_S{}'.format(i + 1), seq) for
                    (i, seq) in enumerate(lib.barcode.sequence.split(','))
                ]
            else:
                seqs = [('', lib.barcode.sequence)]
            for suffix, seq in seqs:
                rows += [
                    '    - name: {}'.format(repr(lib.name + suffix)),
                    '      reference: {}'.format(repr(lib.reference)),
                ]
                if lib.barcode_set and lib.barcode:
                    rows += [
                        '      barcode_set: {}'.format(repr(
                            lib.barcode_set.short_name)),
                        '      barcode:',
                        '        name: {}'.format(repr(lib.barcode.name + suffix)),
                        '        seq: {}'.format(repr(seq)),
                    ]
                if lib.barcode_set2 and lib.barcode2:
                    rows += [
                        '      barcode_set2: {}'.format(repr(
                            lib.barcode_set2.short_name)),
                        '      barcode2:',
                        '        name: {}'.format(repr(lib.barcode2.name)),
                        '        seq: {}'.format(repr(idx2mod(
                            lib.barcode2.sequence))),
                    ]
                rows += [
                    '      lanes: {}'.format(list(sorted(lib.lane_numbers))),
                ]
        return '\n'.join(rows) + '\n'

    def build_v1(self):
        """To bcl2fastq v1 sample sheet CSV file"""
        rows = [['FCID', 'Lane', 'SampleID', 'SampleRef', 'Index',
                 'Description', 'Control', 'Recipe', 'Operator',
                 'SampleProject']]
        if self.flow_cell.is_paired:
            recipe = 'PE_indexing'
        else:
            recipe = 'SE_indexing'
        for lib in self.flow_cell.libraries.order_by('name'):
            if lib.barcode_set.set_type == '10x_genomics':
                seqs = [
                    ('_S{}'.format(i + 1), seq) for
                    (i, seq) in enumerate(lib.barcode.sequence.split(','))
                ]
            else:
                seqs = [('', lib.barcode.sequence)]
            for suffix, seq in seqs:
                for lane_no in sorted(lib.lane_numbers):
                    rows.append([
                        self.flow_cell.vendor_id,
                        lane_no,
                        lib.name + suffix,
                        lib.reference,
                        seq,
                        '',
                        'N',  # not PhiX
                        recipe,
                        self.flow_cell.operator,
                        'Project',
                    ])
        return '\n'.join(','.join(map(str, row)) for row in rows) + '\n'  # noqa

    def build_v2(self):
        """To bcl2fastq v2 sample sheet CSV file"""
        date = self.flow_cell.run_date.strftime("%y/%m/%d")
        rows = [
            ['[Header]'],
            ['IEMFileVersion', '4'],
            ['Investigator Name', self.flow_cell.operator],
            ['Experiment Name', 'Project'],
            ['Date', date],
            ['Workflow', 'GenerateFASTQ'],
            ['Applications', 'FASTQ Only'],
            ['Assay', 'TruSeq HT'],
            ['Description', ''],
            [],
            ['[Reads]'],
            [str(self.flow_cell.read_length)],
        ]
        if self.flow_cell.is_paired:
            rows.append([str(self.flow_cell.read_length)])
        rows += [
            [],
            ['[Data]'],
            ['Lane', 'Sample_ID', 'Sample_Name', 'Sample_Plate', 'Sample_Well',
             'i7_Index_ID', 'index', 'Sample_Project', 'Description'],
        ]
        for lib in self.flow_cell.libraries.order_by('name'):
            if lib.barcode_set.set_type == '10x_genomics':
                seqs = [
                    ('_S{}'.format(i + 1), seq) for
                    (i, seq) in enumerate(lib.barcode.sequence.split(','))
                ]
            else:
                seqs = [('', lib.barcode.sequence)]
            for suffix, seq in seqs:
                for lane_no in sorted(lib.lane_numbers):
                    rows.append([
                        lane_no,
                        lib.name + suffix,
                        '',
                        '',
                        '',
                        lib.barcode.name,
                        seq,
                        'Project',
                        '',
                    ])
        return '\n'.join(','.join(map(str, row)) for row in rows) + '\n'  # noqa
