from rest_framework import serializers
from dry_rest_permissions.generics import DRYPermissionsField

from ..models import BarcodeSetEntry, BarcodeSet, FlowCell, SequencingMachine
from ...threads.models import Message


class SequencingMachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequencingMachine
        fields = ('pk', 'created', 'modified', 'vendor_id', 'label', 'description',
                  'machine_model', 'slot_count', 'dual_index_workflow')
        read_only_fields = ('pk', 'created', 'modified')


class BarcodeSetEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = BarcodeSetEntry
        fields = ('pk', 'created', 'modified', 'name', 'sequence')
        read_only_fields = ('pk', 'created', 'modified')


class BarcodeSetSerializer(serializers.ModelSerializer):
    sorted_entries = BarcodeSetEntrySerializer(many=True, read_only=True)

    class Meta:
        model = BarcodeSet
        fields = ('pk', 'created', 'modified', 'name', 'short_name', 'description',
                  'sorted_entries')
        read_only_fields = ('pk', 'created', 'modified')


class FlowCellSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()
    _permissions = DRYPermissionsField()

    class Meta:
        model = FlowCell
        fields = ('pk', 'owner', 'created', 'modified', 'run_date', 'run_number', 'slot',
                  'vendor_id', 'label', 'description', 'num_lanes', 'status', 'operator',
                  'is_paired', 'index_read_count', 'rta_version', 'read_length',
                  'info_adapters', 'info_quality_scores', '_permissions')
        read_only_fields = ('pk', 'owner', 'created', 'modified', 'info_adapters',
                            'info_quality_scores')


class FlowCellPostSequencingSerializer(serializers.ModelSerializer):
    """Serializer that provides write access to the ``info_adapters`` and ``info_quality_scores``
    fields.
    """
    _permissions = DRYPermissionsField()

    # TODO: add validation to JSON, for now we trust authenticated users as long as the JSON
    # TODO: is valid

    class Meta:
        model = FlowCell
        fields = ('pk', 'info_adapters', 'info_quality_scores', 'status', '_permissions')
        read_only_fields = ('pk', '_permissions')


class FlowCellMessageSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Message
        fields = ('pk', 'created', 'modified', 'title', 'body', 'mime_type',
                  'author')
        read_only_fields = ('pk', 'author', 'created', 'modified')
