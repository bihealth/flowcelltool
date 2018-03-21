from rest_framework import serializers
from dry_rest_permissions.generics import DRYPermissionsField

from ..models import BarcodeSetEntry, BarcodeSet, FlowCell, SequencingMachine
from ...threads.models import Message


class SequencingMachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequencingMachine
        fields = ('uuid', 'created', 'modified', 'vendor_id', 'label', 'description',
                  'machine_model', 'slot_count', 'dual_index_workflow')
        read_only_fields = ('uuid', 'created', 'modified')


class BarcodeSetEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = BarcodeSetEntry
        fields = ('uuid', 'created', 'modified', 'name', 'sequence')
        read_only_fields = ('uuid', 'created', 'modified')


class BarcodeSetSerializer(serializers.ModelSerializer):
    entries = BarcodeSetEntrySerializer(many=True, read_only=True)
    _permissions = DRYPermissionsField()

    class Meta:
        model = BarcodeSet
        fields = ('uuid', 'created', 'modified', 'name', 'short_name', 'description',
                  'entries', '_permissions')
        read_only_fields = ('uuid', 'created', 'modified')


class FlowCellMessageSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Message
        fields = ('uuid', 'created', 'modified', 'title', 'body', 'mime_type',
                  'author')
        read_only_fields = ('uuid', 'author', 'created', 'modified')


class FlowCellSerializer(serializers.ModelSerializer):
    sequencing_machine = serializers.UUIDField(source='sequencing_machine.uuid')
    owner = serializers.StringRelatedField()
    _permissions = DRYPermissionsField()

    class Meta:
        model = FlowCell
        fields = ('uuid', 'owner', 'created', 'modified', 'run_date', 'run_number', 'slot',
                  'sequencing_machine', 'vendor_id', 'label', 'description', 'num_lanes', 'status',
                  'operator', 'rta_version', 'info_planned_reads', 'info_final_reads',
                  'info_adapters', 'info_quality_scores', '_permissions')
        read_only_fields = ('uuid', 'owner', 'created', 'modified')

    def create(self, validated_data):
        sequencing_machine = SequencingMachine.objects.get(
            uuid=str(validated_data.pop('sequencing_machine').get('uuid')))
        instance = FlowCell.objects.create(
            sequencing_machine=sequencing_machine,
            **validated_data)
        return instance


class FlowCellPostSequencingSerializer(serializers.ModelSerializer):
    """Serializer that provides write access to the ``info_adapters`` and ``info_quality_scores``
    fields.
    """
    _permissions = DRYPermissionsField()

    # TODO: add validation to JSON, for now we trust authenticated users as long as the JSON
    # TODO: is valid

    class Meta:
        model = FlowCell
        fields = ('uuid', 'info_adapters', 'info_quality_scores', 'status', '_permissions')
        read_only_fields = ('uuid', '_permissions')
