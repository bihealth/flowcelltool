from rest_framework import serializers
from django.db import transaction
from django.shortcuts import get_object_or_404

from ..models import BarcodeSetEntry, BarcodeSet, FlowCell, Library, SequencingMachine
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

    class Meta:
        model = BarcodeSet
        fields = ('uuid', 'created', 'modified', 'name', 'short_name', 'description',
                  'entries')
        read_only_fields = ('uuid', 'created', 'modified')


class FlowCellMessageSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Message
        fields = ('uuid', 'created', 'modified', 'title', 'body', 'mime_type',
                  'author')
        read_only_fields = ('uuid', 'author', 'created', 'modified')


class LibrarySerializer(serializers.ModelSerializer):
    barcode_set = serializers.UUIDField(source='barcode_set.uuid', default=None)
    barcode = serializers.UUIDField(source='barcode.uuid', default=None)
    barcode_set2 = serializers.UUIDField(source='barcode_set2.uuid', default=None)
    barcode2 = serializers.UUIDField(source='barcode2.uuid', default=None)

    class Meta:
        model = Library
        fields = ('uuid', 'name', 'reference', 'barcode_set', 'barcode', 'barcode_set2',
                  'barcode2', 'lane_numbers')


class SomeKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """Allows to dump non-PK uuid for many related."""

    def __init__(self, related_key, **kwargs):
        self.related_key = related_key
        super().__init__(**kwargs)

    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        if self.pk_field is not None:
            return self.pk_field.to_representation(getattr(value, self.related_key))
        return value.pk



class FlowCellSerializer(serializers.ModelSerializer):
    sequencing_machine = serializers.UUIDField(source='sequencing_machine.uuid')
    owner = serializers.StringRelatedField()
    libraries = LibrarySerializer(many=True)
    messages = SomeKeyRelatedField(
        related_key='uuid', pk_field=serializers.UUIDField(), many=True, read_only=True)

    class Meta:
        model = FlowCell
        fields = ('uuid', 'owner', 'created', 'modified', 'run_date', 'run_number', 'slot',
                  'sequencing_machine', 'vendor_id', 'label', 'description', 'num_lanes',
                  'operator', 'rta_version', 'info_planned_reads', 'info_final_reads',
                  'info_adapters', 'info_quality_scores',
                  'status_sequencing', 'status_conversion', 'status_delivery',
                  'delivery_type', 'libraries', 'messages')
        read_only_fields = ('uuid', 'owner', 'created', 'modified')

    def create(self, validated_data):
        sequencing_machine = validated_data.pop('sequencing_machine')
        libraries = validated_data.pop('libraries', [])
        sequencing_machine = get_object_or_404(
            SequencingMachine, uuid=sequencing_machine.get('uuid'))
        with transaction.atomic():
            instance = super().create(validated_data)
            instance.owner = self.context['request'].user
            instance.sequencing_machine = sequencing_machine
#            for library in libraries:
#                barcode_set = library.pop('barcode_set', None)
#                if barcode_set:
#                    barcode_set = get_object_or_404(BarcodeSet, uuid=barcode_set)
#                barcode = library.pop('barcode', None)
#                if barcode:
#                    barcode = get_object_or_404(BarcodeSetEntry, uuid=barcode)
#                barcode_set2 = library.pop('barcode_set2', None)
#                if barcode_set2:
#                    barcode_set2 = get_object_or_404(BarcodeSet, uuid=barcode_set2)
#                barcode = library.pop('barcode2', None)
#                if barcode2:
#                    barcode2 = get_object_or_404(BarcodeSetEntry, uuid=barcode2)
#                instance.libraries.create(
#                    barcode=barcode, barcode_set=barcode_set, barcode2=barcode2,
#                    barcode_set2=barcode_set2, **library)
            instance.save()
        return instance

    def update(self, instance, validated_data):
        sequencing_machine = validated_data.pop('sequencing_machine', {})
        libraries = validated_data.pop('libraries', [])
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            if sequencing_machine:
                instance.sequencing_machine = SequencingMachine.objects.get(
                    uuid=str(sequencing_machine.get('uuid')))
#            instance_libs = set(lib.uuid for lib in instance.libraries.all())
#            query_libs = set(lib.uuid for lib in libraries)
#            for uuid in instance_libs - query_libs:  # to be removed
#                instance.libraries.get(uuid=uuid).delete()
#            for lib in libraries:
#                if lib['uuid'] in query_libs - instance_libs:  # new library
#                    instance.libraries.create(**lib)
            instance.save()
        return instance


class FlowCellPostSequencingSerializer(serializers.ModelSerializer):
    """Serializer that provides write access to the ``info_adapters`` and ``info_quality_scores``
    fields.
    """
    # TODO: add validation to JSON, for now we trust authenticated users as long as the JSON
    # TODO: is valid

    class Meta:
        model = FlowCell
        fields = ('uuid', 'info_adapters', 'info_quality_scores', 'status', '_permissions')
        read_only_fields = ('uuid')
