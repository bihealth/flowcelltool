from django.contrib import admin

from .models import SequencingMachine, FlowCell, BarcodeSet, BarcodeSetEntry

admin.site.register(SequencingMachine)
admin.site.register(FlowCell)
admin.site.register(BarcodeSet)
admin.site.register(BarcodeSetEntry)
