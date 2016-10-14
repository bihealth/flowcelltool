from django import forms
from django.db import transaction
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from crispy_forms.helper import FormHelper

from . import models

# Form for importing BarcodeSet from JSON -------------------------------------


class BarcodeSetImportForm(forms.Form):
    """The form used for uploading serialized barcode sets from JSON"""

    #: File upload field
    json_file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.template_pack = 'bootstrap4'
        self.helper.form_tag = False


# BarcodeSetEntry multi-edit related ------------------------------------------

#: Number of additional barcode set entry forms (= table rows) to create
EXTRA_BARCODE_FORMS = 10

#: Fields to use for the barcode set forms (= table rows)
BARCODE_SET_ENTRY_FIELDS = ('name', 'sequence')


class BarcodeSetEntryForm(forms.ModelForm):
    """Form for handling barcode entries (table rows in the form set)"""

    class Meta:
        model = models.BarcodeSetEntry
        fields = BARCODE_SET_ENTRY_FIELDS


class BaseBarcodeSetEntryFormSet(BaseModelFormSet):
    """Base class for the form set to create"""

    def __init__(self, *args, **kwargs):
        self.barcode_set = kwargs.pop('barcode_set')
        super().__init__(*args, **kwargs)
        self.queryset = self.barcode_set.entries.order_by('name').all()

    def save(self, *args, **kwargs):
        """Handle saving of form set, including support for deleting barcode
        set entries
        """
        with transaction.atomic():
            entries = super().save(*args, commit=False, **kwargs)
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
    form=BarcodeSetEntryForm,
    formset=BaseBarcodeSetEntryFormSet,
    fields=BARCODE_SET_ENTRY_FIELDS,
    extra=EXTRA_BARCODE_FORMS)


# Form for importing FlowCell from JSON ---------------------------------------


class FlowCellImportForm(forms.Form):
    """The form used for uploading serialized flow cells from JSON"""

    #: File upload field
    json_file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.template_pack = 'bootstrap4'
        self.helper.form_tag = False


# FlowCell related ------------------------------------------------------------


class FlowCellForm(forms.ModelForm):

    class Meta:

        model = models.FlowCell

        fields = ('name', 'description', 'num_lanes', 'status', 'operator',
                  'is_paired', 'index_read_count', 'rta_version',
                  'read_length')


class LibrariesPrefillForm(forms.Form):
    """Helper form for filling out forms with barcodes"""

    #: Choice field for selecting first barcode
    barcode1 = forms.ModelChoiceField(
        required=False,
        queryset=models.BarcodeSet.objects.order_by('name').all())

    #: Choice field for selecting second barcode
    barcode2 = forms.ModelChoiceField(
        required=False,
        queryset=models.BarcodeSet.objects.order_by('name').all())


# Library multi-edit related -------------------------------------------------

#: Number of additional barcode set entry forms (= table rows) to create
EXTRA_LIBRARY_FORMS = 10

#: Fields to use for the library forms (= table rows)
LIBRARY_FIELDS = ('name', 'reference', 'barcode_set', 'barcode',
                  'barcode_set2', 'barcode2', 'lane_numbers')


class BarcodeSelect(forms.Select):
    """Barcode selection, adds "data-barcode-set" attribute to <option>

    This is required for the form JavaScript to limit selections to the
    barcodes from the given barcode sets.
    """

    def render_option(self, selected_choices, option_value, option_label):
        if option_value is None:
            option_value = ''
        if option_value:
            set_id = models.BarcodeSetEntry.objects.get(
                pk=option_value).barcode_set.id
        else:
            set_id = ''
        option_value = force_text(option_value)
        if option_value in selected_choices:
            selected_html = mark_safe(' selected="selected"')
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        return format_html('<option data-set-id="{}" value="{}"{}>{}</option>',
                           set_id,
                           option_value,
                           selected_html,
                           force_text(option_label))


class LibraryForm(forms.ModelForm):
    """Form for handling library entries (table rows in the form set)"""

    barcode = forms.ModelChoiceField(
        required=False,
        queryset=models.BarcodeSetEntry.objects.order_by('name'),
        widget=BarcodeSelect)
    barcode2 = forms.ModelChoiceField(
        required=False,
        queryset=models.BarcodeSetEntry.objects.order_by('name'),
        widget=BarcodeSelect)

    def __init__(self, *args, **kwargs):
        # Pre-set the lane numbers, required for Django Formsets to work
        # with uninitialized values
        kwargs.setdefault('initial', {})
        if 'instance' in kwargs:
            kwargs['initial']['lane_numbers'] = kwargs['instance'].lane_numbers
        else:
            kwargs['initial']['lane_numbers'] = []
        super().__init__(*args, **kwargs)

    class Meta:
        model = models.Library
        fields = LIBRARY_FIELDS


class BaseLibraryFormSet(BaseModelFormSet):
    """Base class for the form set to create"""

    def __init__(self, *args, **kwargs):
        self.flow_cell = kwargs.pop('flow_cell')
        super().__init__(*args, **kwargs)
        self.queryset = self.flow_cell.libraries.order_by('name').all()

    def save(self, *args, **kwargs):
        """Handle saving of form set, including support for deleting barcode
        set entries
        """
        with transaction.atomic():
            entries = super().save(*args, commit=False, **kwargs)
            for entry in entries:
                entry.flow_cell = self.flow_cell
                entry.save()
            for entry in self.deleted_objects:
                entry.delete()
            return entries


#: Form set for barcodes, constructed with factory function
LibraryFormSet = modelformset_factory(
    models.Library,
    can_delete=True,
    form=LibraryForm,
    formset=BaseLibraryFormSet,
    fields=LIBRARY_FIELDS,
    extra=EXTRA_LIBRARY_FORMS)
