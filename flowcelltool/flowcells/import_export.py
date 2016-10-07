# -*- coding: utf-8 -*-
"""Code for importing and exporting database records to YAML/JSON"""

from collections import OrderedDict
import json

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import BarcodeSet, FlowCell, Library


__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


# BarcodeSet related ----------------------------------------------------------


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


class BarcodeSetLoader:
    """Helper class loading BarcodeSet objects from JSON and storing them
    in the database

    BarcodeSet objects can be serialized using BarcodeSetDumper
    """

    @classmethod
    def run(klass, json_string):
        """Load BarcodeSet object form json_string"""
        deserialized = json.loads(json_string)
        with transaction.atomic():
            barcode_set = BarcodeSet(
                name=deserialized['name'],
                short_name=deserialized['short_name'],
                description=deserialized['description'])
            barcode_set.save()
            for entry in deserialized['entries']:
                barcode_set.entries.create(
                    name=entry['name'],
                    sequence=entry['sequence']).save()
            return barcode_set


# FlowCell related ------------------------------------------------------------


class FlowCellDumper:
    """Helper class for dumping FlowCell objects to JSON

    They can be imported later with FlowCellLoader again.
    """

    @classmethod
    def run(klass, flow_cell):
        """Return JSON dump of FlowCell in flow_cell as string"""
        # Get base fields
        result = OrderedDict()
        for key in ('name', 'description', 'num_lanes',
                      'status', 'operator', 'is_paired',
                      'index_read_count', 'rta_version',
                      'read_length'):
            result[key] = getattr(flow_cell, key)
        # Get barcode set entries
        result['libraries'] = []
        for entry in flow_cell.libraries.order_by('name'):
            odict = OrderedDict(
                [
                    ('name', entry.name),
                    ('reference', entry.reference),
                    ('barcode_set', None),
                    ('barcode_name', None),
                    ('barcode_sequence', None),
                    ('barcode_set2', None),
                    ('barcode_name2', None),
                    ('barcode_sequence2', None),
                    ('lane_numbers', entry.lane_numbers),
                ])
            if entry.barcode:
                odict.update(OrderedDict([
                    ('barcode_set', entry.barcode_set.short_name),
                    ('barcode_name', entry.barcode.name),
                    ('barcode_sequence', entry.barcode.sequence),
                ]))
            if entry.barcode2:
                odict.update(OrderedDict([
                    ('barcode_set2', entry.barcode_set2.short_name),
                    ('barcode_name2', entry.barcode2.name),
                    ('barcode_sequence2', entry.barcode2.sequence),
                ]))
            result['libraries'].append(odict)
        return json.dumps(result, indent=2) + '\n'


class FlowCellLoader:
    """Helper class loading FlowCell objects from JSON and storing them
    in the database

    FlowCell objects can be serialized using FlowCellDumper
    """

    @classmethod
    def run(klass, json_string):
        """Load FlowCell object form json_string"""
        deserialized = json.loads(json_string)
        with transaction.atomic():
            flow_cell = FlowCell(
                name=deserialized['name'],
                description=deserialized['description'],
                num_lanes=deserialized['num_lanes'],
                status=deserialized['status'],
                operator=deserialized['operator'],
                is_paired=deserialized['is_paired'],
                index_read_count=deserialized['index_read_count'],
                rta_version=deserialized['rta_version'],
                read_length=deserialized['read_length'])
            flow_cell.save()
            for library in deserialized['libraries']:
                barcode_set, barcode = None, None
                if library.get('barcode_set'):
                    barcode_set = get_object_or_404(
                        BarcodeSet, short_name=library.get('barcode_set'))
                    qs = barcode_set.entries.filter(
                        name=library.get('barcode_name'))
                    if qs.count() != 1:
                        raise ValidationError('Invalid barcode')
                    barcode = qs[0]
                barcode_set2, barcode2 = None, None
                if library.get('barcode_set2'):
                    barcode_set2 = get_object_or_404(
                        BarcodeSet, short_name=library.get('barcode_set2'))
                    qs = barcode_set.entries.filter(
                        name=library.get('barcode_name2'))
                    if qs.count() != 1:
                        raise ValidationError('Invalid barcode 2')
                    barcode2 = qs[0]
                flow_cell.libraries.create(
                    name=library['name'],
                    reference=library['reference'],
                    lane_numbers=library['lane_numbers'],
                    barcode_set=barcode_set,
                    barcode=barcode,
                    barcode_set2=barcode_set2,
                    barcode2=barcode2)
            return flow_cell
