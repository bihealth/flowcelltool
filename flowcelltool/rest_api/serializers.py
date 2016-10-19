# -*- coding: utf-8 -*-
"""DRF serializers for the models
"""

from rest_framework import serializers
from generic_relations.relations import GenericRelatedField

from ..flowcells import models
from ..threads import models as threads_models
from ..users import models as users_models


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = users_models.User
        fields = ('username',)


class SequencingMachineSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.SequencingMachine
        fields = ('pk', 'url', 'created', 'updated', 'vendor_id', 'label',
                  'description', 'machine_model', 'slot_count',
                  'dual_index_workflow')


class BarcodeSetSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.BarcodeSet
        fields = ('pk', 'url', 'created', 'updated', 'name', 'short_name',
                  'description', 'entries')


class BarcodeSetEntrySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.BarcodeSetEntry
        fields = ('pk', 'url', 'created', 'updated', 'name', 'sequence',
                  'barcode_set')


class FlowCellSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.FlowCell
        fields = ('pk', 'url', 'created', 'updated', 'owner', 'name',
                  'description', 'sequencing_machine', 'num_lanes',
                  'status', 'operator', 'is_paired', 'index_read_count',
                  'rta_version', 'read_length', 'libraries')


class LibrarySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Library
        fields = ('pk', 'url', 'created', 'updated', 'name', 'reference',
                  'barcode_set', 'barcode', 'barcode_set2', 'barcode2',
                  'lane_numbers', 'flow_cell')


class MessageSerializer(serializers.HyperlinkedModelSerializer):
    thread_object = GenericRelatedField({
        models.FlowCell: serializers.HyperlinkedRelatedField(
            queryset = models.FlowCell.objects.all(),
            view_name='flowcell-detail',
        )
    })

    class Meta:
        model = threads_models.Message
        fields = ('pk', 'url', 'created', 'updated', 'title', 'body',
                  'thread_object', 'attachments')


class AttachmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = threads_models.Attachment
        fields = ('pk', 'url', 'created', 'updated', 'message', 'payload')
