# -*- coding: utf-8 -*-
"""DRF views"""

from rest_framework import viewsets

from ..flowcells import models
from ..users.models import User
from . import serializers


class UserViewSet(viewsets.ModelViewSet):
    """API endpoint for User"""

    queryset = User.objects.all().order_by('date_joined')
    serializer_class = serializers.UserSerializer


class SequencingMachineViewSet(viewsets.ModelViewSet):
    """API endpoint for SequencingMachine"""

    queryset = models.SequencingMachine.objects.all().order_by('created_at')
    serializer_class = serializers.SequencingMachineSerializer


class BarcodeSetViewSet(viewsets.ModelViewSet):
    """API endpoint for BarcodeSet"""

    queryset = models.BarcodeSet.objects.all().order_by('created_at')
    serializer_class = serializers.BarcodeSetSerializer


class BarcodeSetEntryViewSet(viewsets.ModelViewSet):
    """API endpoint for BarcodeSetEntry"""

    queryset = models.BarcodeSetEntry.objects.all().order_by('created_at')
    serializer_class = serializers.BarcodeSetEntrySerializer


class FlowCellViewSet(viewsets.ModelViewSet):
    """API endpoint for FlowCell"""

    queryset = models.FlowCell.objects.all().order_by('created_at')
    serializer_class = serializers.FlowCellSerializer


class LibraryViewSet(viewsets.ModelViewSet):
    """API endpoint for Library"""

    queryset = models.Library.objects.all().order_by('created_at')
    serializer_class = serializers.LibrarySerializer


class MessageViewSet(viewsets.ModelViewSet):
    """API endpoint for Message"""

    queryset = models.Message.objects.all().order_by('created_at')
    serializer_class = serializers.MessageSerializer
