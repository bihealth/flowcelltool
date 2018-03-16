from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from .. import import_export
from ..models import BarcodeSet, FlowCell, SequencingMachine
from .serializers import (
    BarcodeSetSerializer,
    FlowCellMessageSerializer,
    FlowCellSerializer,
    SequencingMachineSerializer)


# SequencingMachine API Views -------------------------------------------------


class SequencingMachineListApiView(ListAPIView):
    """API view for listing sequencing machines."""
    queryset = SequencingMachine.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SequencingMachineSerializer


class SequencingMachineDetailApiView(RetrieveAPIView):
    """API view for retrieving by vendor ID."""
    lookup_field = 'pk'
    queryset = SequencingMachine.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SequencingMachineSerializer


class SequencingMachineByVendorIdApiView(RetrieveAPIView):
    """API view for retrieving by vendor ID."""
    lookup_field = 'vendor_id'
    queryset = SequencingMachine.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SequencingMachineSerializer


# BarcodeSet API Views --------------------------------------------------------


class BarcodeSetListApiView(ListAPIView):
    """API view for listing barcodes."""
    queryset = BarcodeSet.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = BarcodeSetSerializer


class BarcodeSetDetailApiView(RetrieveAPIView):
    """API view for retrieving by vendor ID."""
    lookup_field = 'pk'
    queryset = BarcodeSet.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = BarcodeSetSerializer


# FlowCell API Views ----------------------------------------------------------


class FlowCellListApiView(ListAPIView):
    """API view for listing flow cells."""
    queryset = FlowCell.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = FlowCellSerializer


class FlowCellDetailApiView(RetrieveAPIView):
    """API view for retrieving by vendor ID."""
    lookup_field = 'pk'
    queryset = FlowCell.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = FlowCellSerializer


class FlowCellByVendorIdApiView(RetrieveAPIView):
    """API view for retrieving by vendor ID."""
    lookup_field = 'vendor_id'
    queryset = FlowCell.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = FlowCellSerializer


import logging
logger = logging.getLogger(__name__)


class FlowCellSampleSheetApiView(RetrieveAPIView):
    """API view for retrieving by vendor ID."""
    lookup_field = 'pk'
    queryset = FlowCell.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = FlowCellSerializer

    def get(self, request, pk, *args, **kwargs):
        sheet_format = request.query_params.get('sheet_format', None)
        gen = import_export.FlowCellSampleSheetGenerator(self.get_object())
        if sheet_format == 'csv_v1':
            content = gen.build_v1()
        elif sheet_format == 'csv_v2':
            content = gen.build_v2()
        else:  # format == 'yaml'
            content = gen.build_yaml()
        return HttpResponse(content, content_type='text/plain; charset=utf-8')


# Message API Views -----------------------------------------------------------


class MessageListApiView(ListAPIView):
    """API view for listing messages."""
    permission_classes = (IsAuthenticated,)
    serializer_class = FlowCellMessageSerializer

    def get_queryset(self):
        flowcell = get_object_or_404(FlowCell, pk=self.kwargs['related_pk'])
        return flowcell.messages.all()
