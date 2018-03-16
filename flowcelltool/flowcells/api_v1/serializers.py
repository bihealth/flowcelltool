from rest_framework import serializers
from generic_relations.relations import GenericRelatedField

from ..models import BarcodeSet, FlowCell, SequencingMachine
from ...threads.models import Message


class SequencingMachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequencingMachine
        fields = ('pk', 'created', 'modified', 'vendor_id', 'label', 'description',
                  'machine_model', 'slot_count', 'dual_index_workflow')


class BarcodeSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = BarcodeSet
        fields = ('pk', 'created', 'modified', 'name', 'short_name', 'description')
        # TODO: sorted entries?


class FlowCellSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlowCell
        fields = ('pk', 'created', 'modified', 'run_date', 'run_number', 'slot', 'vendor_id',
                  'label', 'description', 'num_lanes', 'status', 'operator',
                  'is_paired', 'index_read_count', 'rta_version', 'read_length')
        # TODO: foreign keys?


class FlowCellMessageSerializer(serializers.ModelSerializer):
    # thread_object = GenericRelatedField({
    #     FlowCell: FlowCellSerializer(),
    # })

    class Meta:
        model = Message
        fields = ('pk', 'created', 'modified', 'title', 'body', 'mime_type',
                  # 'thread_object'
                  )
        # TODO: foreign keys?
