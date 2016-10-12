# -*- coding: utf-8 -*-
"""Register flowcells models with admin using django-rule permissions"""

from django.contrib import admin

from rules.contrib.admin import ObjectPermissionsModelAdmin

from .models import SequencingMachine, FlowCell, Library, BarcodeSet, \
    BarcodeSetEntry


# Object-level Permissions Admins based on django-rules -----------------------


class SequencingMachineAdmin(ObjectPermissionsModelAdmin):
    pass


class FlowCellAdmin(ObjectPermissionsModelAdmin):
    pass


class LibraryAdmin(ObjectPermissionsModelAdmin):
    pass


class BarcodeSetAdmin(ObjectPermissionsModelAdmin):
    pass


class BarcodeSetEntryAdmin(ObjectPermissionsModelAdmin):
    pass


# Register Models in admin interface ------------------------------------------

admin.site.register(SequencingMachine, SequencingMachineAdmin)
admin.site.register(FlowCell, FlowCellAdmin)
admin.site.register(Library, LibraryAdmin)
admin.site.register(BarcodeSet, BarcodeSetAdmin)
admin.site.register(BarcodeSetEntry, BarcodeSetEntryAdmin)
