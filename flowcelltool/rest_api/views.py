# -*- coding: utf-8 -*-
"""DRF views"""

from django.http import Http404
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated

from ..flowcells import models
from ..users.models import User
from . import serializers

# Permission Helpers ----------------------------------------------------------


class RulesBackedPermissions(permissions.BasePermission):
    """Enforce permissions via ``django-rules``
    """

    PERMS_MAP = {
        'list': ['{app_label}.list_{model_name}'],
        'create': ['{app_label}.add_{model_name}'],
        'retrieve': ['{app_label}.view_{model_name}'],
        'update': ['{app_label}.change_{model_name}'],
        'partial_update': ['{app_label}.change_{model_name}'],
        'destroy': ['{app_label}.delete_{model_name}'],
    }

    def get_required_permissions(self, action, model_cls):
        """Get required permission based on the request action and model class
        """
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name
        }
        return [perm.format(**kwargs) for perm in self.PERMS_MAP[action]]

    def has_permission(self, request, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        action = view.action or 'retrieve'
        if getattr(view, '_ignore_model_permissions', False):
            return True

        if hasattr(view, 'get_queryset'):
            queryset = view.get_queryset()
        else:
            queryset = getattr(view, 'queryset', None)

        assert queryset is not None, (
            'Cannot apply RulesBackedPermissions on a view that '
            'does not set `.queryset` or have a `.get_queryset()` method.'
        )

        perms = self.get_required_permissions(action, queryset.model)

        return (
            request.user and
            (permissions.is_authenticated(request.user) or
            not self.authenticated_users_only) and
            all(request.user.has_perm(perm) for perm in perms))

    def has_object_permission(self, request, view, obj):
        action = view.action or 'retrieve'
        if hasattr(view, 'get_queryset'):
            queryset = view.get_queryset()
        else:
            queryset = getattr(view, 'queryset', None)

        assert queryset is not None, (
            'Cannot apply DjangoObjectPermissions on a view that '
            'does not set `.queryset` or have a `.get_queryset()` method.'
        )

        model_cls = queryset.model
        perms = self.get_required_permissions(action, model_cls)

        if not all(request.user.has_perm(perm, obj) for perm in perms):
            # If the user does not have permissions we need to determine if
            # they have read permissions to see 403, or not, and simply see
            # a 404 response.

            if request.method in permissions.SAFE_METHODS:
                # Read permissions already checked and failed, no need
                # to make another lookup.
                raise Http404

            read_perms = self.get_required_permissions('retrieve', model_cls)
            if not all(request.user.has_perm(perm, obj)
                       for perm in read_perms):
                raise Http404

            # Has read permissions.
            return False

        return True


# DRF API ViewSets ------------------------------------------------------------


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, RulesBackedPermissions)


class UserViewSet(BaseViewSet):
    """API endpoint for User"""

    queryset = User.objects.all().order_by('date_joined')
    serializer_class = serializers.UserSerializer


class SequencingMachineViewSet(BaseViewSet):
    """API endpoint for SequencingMachine"""

    queryset = models.SequencingMachine.objects.all().order_by('created')
    serializer_class = serializers.SequencingMachineSerializer


class BarcodeSetViewSet(BaseViewSet):
    """API endpoint for BarcodeSet"""

    queryset = models.BarcodeSet.objects.all().order_by('created')
    serializer_class = serializers.BarcodeSetSerializer


class BarcodeSetEntryViewSet(BaseViewSet):
    """API endpoint for BarcodeSetEntry"""

    queryset = models.BarcodeSetEntry.objects.all().order_by('created')
    serializer_class = serializers.BarcodeSetEntrySerializer


class FlowCellViewSet(BaseViewSet):
    """API endpoint for FlowCell"""

    queryset = models.FlowCell.objects.all().order_by('created')
    serializer_class = serializers.FlowCellSerializer


class LibraryViewSet(BaseViewSet):
    """API endpoint for Library"""

    queryset = models.Library.objects.all().order_by('created')
    serializer_class = serializers.LibrarySerializer


class MessageViewSet(BaseViewSet):
    """API endpoint for Message"""

    queryset = models.Message.objects.all().order_by('created')
    serializer_class = serializers.MessageSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class AttachmentViewSet(BaseViewSet):
    """API endpoint for Message"""

    queryset = models.Attachment.objects.all().order_by('created')
    serializer_class = serializers.AttachmentSerializer
