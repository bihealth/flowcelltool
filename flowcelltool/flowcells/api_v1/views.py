from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.reverse import reverse

from .. import import_export
from ..models import BarcodeSet, FlowCell, SequencingMachine
from ...threads.models import Message
from .serializers import (
    BarcodeSetSerializer,
    FlowCellMessageSerializer,
    FlowCellSerializer,
    SequencingMachineSerializer,
    FlowCellPostSequencingSerializer)


# Mixin for retrieving by UUID ------------------------------------------------


class RetrieveByUuidMixin:
    lookup_field = 'uuid'


# SequencingMachine API Views -------------------------------------------------


class SequencingMachineViewSet(
        RetrieveByUuidMixin, viewsets.ReadOnlyModelViewSet):
    """(Read only) view set for sequencing machines."""

    queryset = SequencingMachine.objects.all()
    serializer_class = SequencingMachineSerializer


# BarcodeSet API Views --------------------------------------------------------


class BarcodeSetViewSet(
        RetrieveByUuidMixin, viewsets.ReadOnlyModelViewSet):
    """(Read only) view set for barcodes."""

    queryset = BarcodeSet.objects.all()
    serializer_class = BarcodeSetSerializer


# FlowCell API Views ----------------------------------------------------------


class FlowCellViewSet(
        RetrieveByUuidMixin, viewsets.ReadOnlyModelViewSet):
    """(Read only) view set for flow cells."""

    queryset = FlowCell.objects.all()
    serializer_class = FlowCellSerializer

    def by_vendor_id(self, request, vendor_id=None):
        flowcell = get_object_or_404(self.queryset, vendor_id=vendor_id)
        # Because this does not fit list_route or detail_route, we have to check permissions
        # manually.
        self.check_object_permissions(request, flowcell)
        return Response(self.get_serializer(flowcell).data)

    @detail_route()
    def sample_sheet(self, request, uuid=None):
        sheet_format = request.query_params.get('sheet_format', None)
        gen = import_export.FlowCellSampleSheetGenerator(self.get_object())
        if sheet_format == 'csv_v1':
            content = gen.build_v1()
        elif sheet_format == 'csv_v2':
            content = gen.build_v2()
        else:  # format == 'yaml'
            content = gen.build_yaml()
        return HttpResponse(content, content_type='text/plain; charset=utf-8')

    @detail_route(methods=('post',))
    def add_message(self, request, uuid=None):
        """Adding message to flowcell."""
        # This does not fit list_route or detail_route, we have to check permissions manually.
        if not request.user.has_perm('threads.add_message'):
            raise PermissionDenied('Access not allowed')
        # Otherwise, just add the message to flow cell.
        flowcell = get_object_or_404(self.get_queryset(), uuid=uuid)
        with transaction.atomic():
            msg = Message.objects.create(
                author=request.user,
                content_type=ContentType.objects.get_for_model(flowcell),
                object_id=flowcell.uuid,
                title=request.data.get('title'),
                body=request.data.get('body'))
            for f in request.data.getlist('attachments'):
                msg.attachments.create(payload=f)
        return HttpResponseRedirect(redirect_to=reverse(
            'flowcell-detail', kwargs={'uuid': uuid}, request=request))


class FlowCellUpdateView(APIView):
    """View for updating the ``status``, ``info_adapters``, and ``info_quality_scores`` fields."""

    #: Permissions will be checked manually beyond being logged in.
    permission_classes = (IsAuthenticated,)

    def post(self, request, uuid):
        flowcell = get_object_or_404(FlowCell, uuid=uuid)
        if not request.user.has_perm('flowcells.change_flowcell', flowcell):
            raise PermissionDenied('Access not allowed')
        print(request.data)
        serializer = FlowCellPostSequencingSerializer(flowcell, data=request.data)
        serializer.is_valid(True)
        serializer.save()
        return HttpResponseRedirect(redirect_to=reverse(
            'flowcell-detail', kwargs={'uuid': uuid}, request=request))


# Message API Views -----------------------------------------------------------


class FlowCellMessageViewSet(
        RetrieveByUuidMixin, viewsets.ReadOnlyModelViewSet):
    """(Read only) view set for messages."""

    queryset = Message.objects.all()
    serializer_class = FlowCellMessageSerializer
