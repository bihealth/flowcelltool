from django import forms
from django.db import transaction
from django.forms.models import BaseModelFormSet, modelformset_factory

from crispy_forms.helper import FormHelper

from . import models


#: Number of additional barcode set entry forms (= table rows) to create
EXTRA_BARCODE_FORMS = 10


class BarcodeSetImportForm(forms.Form):
    """The form used for uploading serialized barcode sets from JSON"""

    #: File upload field
    json_file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.template_pack = 'bootstrap4'
        self.helper.form_tag = False


class BarcodeSetEntryForm(forms.ModelForm):
    """Form for handling barcode entries (table rows in the form set)"""

    class Meta:
        model = models.BarcodeSetEntry
        fields = ('name', 'sequence')


class BaseBarcodeSetEntryFormSet(BaseModelFormSet):
    """Base class for the form set to create"""

    def __init__(self, *args, **kwargs):
        self.barcode_set = kwargs.pop('barcode_set')
        super().__init__(*args, **kwargs)
        self.queryset = self.barcode_set.entries.order_by('name').all()

    def save(self):
        """Handle saving of form set, including support for deleting barcode
        set entries
        """
        with transaction.atomic():
            entries = super().save(commit=False)
            for entry in entries:
                entry.barcode_set = self.barcode_set
                entry.save()
            for entry in self.deleted_objects:
                entry.delete()
            return entries


#: Form set for barcodes, constructed with factory function
BarcodeSetEntryFormSet = modelformset_factory(
    models.BarcodeSetEntry,
    can_delete=True,
    form=BarcodeSetEntryForm, formset=BaseBarcodeSetEntryFormSet,
    fields=('name', 'sequence'),
    extra=EXTRA_BARCODE_FORMS)
