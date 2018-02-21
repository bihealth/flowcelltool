# -*- coding: utf-8 -*-

import datetime
import re

from django import forms
from django.db import transaction
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.forms.models import ModelChoiceIterator, ModelChoiceField
from django.forms.fields import ChoiceField
from django.core.validators import RegexValidator

from crispy_forms.helper import FormHelper

from . import models
from .widgets import IntegerRangeField


# Helper code -----------------------------------------------------------------


def get_object_or_none(klass, *args, **kwargs):
    if hasattr(klass, '_default_manager'):
        queryset = klass._default_manager.all()
    else:
        queryset = klass
    try:
        return queryset.get(*args, **kwargs)
    except AttributeError:
        klass__name = (
            klass.__name__
            if isinstance(klass, type)
            else klass.__class__.__name__)
        raise ValueError(
            "First argument to get_object_or_404() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )
    except queryset.model.DoesNotExist:
        return None


# Advanced ModelChoice fields -------------------------------------------------


class AdvancedModelChoiceIterator(ModelChoiceIterator):
    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label, None)
        queryset = self.queryset.all()
        # Can't use iterator() when queryset uses prefetch_related()
        if not queryset._prefetch_related_lookups:  # noqa
            queryset = queryset.iterator()
        for obj in queryset:
            yield self.choice(obj)

    def choice(self, obj):
        return (self.field.prepare_value(obj),
                self.field.label_from_instance(obj), obj)


class AdvancedModelChoiceField(ModelChoiceField):
    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices

        return AdvancedModelChoiceIterator(self)

    choices = property(_get_choices, ChoiceField._set_choices)


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

#: Regular expression for flow cell names
FLOW_CELL_NAME_RE = (
    r'^(?P<date>\d{6,6})'
    r'_(?P<machine_name>[^_]+)'
    r'_(?P<run_no>\d+)'
    r'_(?P<slot>\w)'
    r'_(?P<vendor_id>[^_]+)'
    r'(_(?P<label>.+))?$')


class FlowCellForm(forms.ModelForm):
    """Custom form for manipulating FlowCell objects

    We need a special form to tokenize/untokenize the flow cell name to/from
    properties.
    """

    #: Special field with the flow cell name.  The different tokens
    #: will be extracted in the form's logic
    name = forms.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                FLOW_CELL_NAME_RE,
                message=('Invalid flow cell name. Did you forgot the '
                         'underscore between the slot and the vendor ID?'))],
        help_text=('The full flow cell name, e.g., '
                   '160303_ST-K12345_0815_A_BCDEFGHIXX_LABEL'))

    class Meta:
        model = models.FlowCell

        fields = ('name', 'description', 'num_lanes', 'status', 'operator',
                  'demux_operator',
                  'is_paired', 'index_read_count', 'rta_version',
                  'read_length')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['name'].initial = self.instance.get_full_name()

    def clean(self):
        if 'name' not in self.cleaned_data:
            return self.cleaned_data  # give up, wrong format
        name_dict = re.match(
            FLOW_CELL_NAME_RE, self.cleaned_data.pop('name')).groupdict()
        self.cleaned_data['run_date'] = datetime.datetime.strptime(
            name_dict['date'], '%y%m%d').date()
        self.cleaned_data['sequencing_machine'] = get_object_or_none(
            models.SequencingMachine, vendor_id=name_dict['machine_name'])
        if self.cleaned_data['sequencing_machine'] is None:
            self.add_error('name', 'Unknown sequencing machine')
        self.cleaned_data['run_number'] = int(name_dict['run_no'])
        self.cleaned_data['slot'] = name_dict['slot']
        self.cleaned_data['vendor_id'] = name_dict['vendor_id']
        self.cleaned_data['label'] = name_dict['label']
        return self.cleaned_data

    def save(self, *args, **kwargs):
        for key in ('run_date', 'sequencing_machine', 'run_number', 'slot',
                    'vendor_id', 'label'):
            setattr(self.instance, key, self.cleaned_data[key])
        return super().save(*args, **kwargs)


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

    def render_options(self, selected_choices):
        # Normalize to strings.
        selected_choices = set(force_text(v) for v in selected_choices)
        output = []
        for option_value, option_label, option_model in self.choices:
            if isinstance(option_label, (list, tuple)):
                output.append(format_html(
                    '<optgroup label="{}">', force_text(option_value)))
                for option in option_label:
                    output.append(self.render_option(
                        selected_choices, option, option_model))
                output.append('</optgroup>')
            else:
                output.append(self.render_option(
                    selected_choices, option_value, option_label,
                    option_model))
        return '\n'.join(output)

    def render_option(self, selected_choices, option_value, option_label,
                      option_model):
        if option_value is None:
            option_value = ''
        option_value = force_text(option_value)
        if option_value in selected_choices:
            selected_html = mark_safe(' selected="selected"')
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        return format_html('<option data-set-id="{}" value="{}"{}>{}</option>',
                           '',
                           option_value,
                           selected_html,
                           force_text(option_label))


class LibraryForm(forms.ModelForm):
    """Form for handling library entries (table rows in the form set)"""

    barcode_set = forms.ModelChoiceField(
        required=False,
        queryset=models.BarcodeSet.objects.order_by('name'))
    barcode = AdvancedModelChoiceField(
        required=False,
        queryset=models.BarcodeSetEntry.objects.order_by('name'),
        widget=BarcodeSelect)
    barcode_set2 = forms.ModelChoiceField(
        required=False,
        queryset=models.BarcodeSet.objects.order_by('name'))
    barcode2 = AdvancedModelChoiceField(
        required=False,
        queryset=models.BarcodeSetEntry.objects.order_by('name'),
        widget=BarcodeSelect)
    lane_numbers = IntegerRangeField(required=True, min_length=1)

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


# Wizard for XLS copy-and-paste ----------------------------------------------


class PasteTSVForm(forms.Form):
    """First step of the XLS copy-and-paste wizard

    Allows copy and paste of TSV data or providing an upload XLS file
    """

    #: A Textarea for copy and paste
    payload = forms.CharField(
        required=False,
        label='Tab-separated values',
        help_text='Copy-and paste fields from Excel here',
        widget=forms.Textarea)


class PickColumnsForm(forms.Form):
    """Second step in the XLS copy-and-paste wizard

    Allows to select the barcode sets and barcode set entries as well as
    columns for the sets and the row to start at.
    """

    #: Reference to use for all samples
    reference = forms.ChoiceField(
        required=True,
        choices=models.REFERENCE_CHOICES,
        label='Reference/Organism',
        help_text=('Upon import, the same for all samples.  Can be changed '
                   'later on'))

    #: Select column for sample name
    sample_column = forms.IntegerField(
        min_value=1,
        required=True,
        label='Sample column index',
        help_text='The first column has index 1')

    #: Barcode set for barcode 1
    barcode_set = forms.ModelChoiceField(
        required=True,
        label='Barcode set 1',
        queryset=models.BarcodeSet.objects.order_by('name'))

    #: Select column for barcode 1
    barcode_column = forms.IntegerField(
        min_value=1,
        required=False,
        label='Barcode 1 column index',
        help_text='Leave empty for no barcodes. The first column has index 1')

    #: Barcode set for barcode 2
    barcode_set2 = forms.ModelChoiceField(
        required=False,
        label='Barcode set 2',
        queryset=models.BarcodeSet.objects.order_by('name'),
        help_text='Leave empty for no secondary barcodes')

    #: Select column for barcode 2
    barcode2_column = forms.IntegerField(
        min_value=1,
        required=False,
        label='Barcode 2 column index',
        help_text=('Leave empty for no secondary barcodes. The first column '
                   'has index 1'))

    #: Select row number to start at
    first_row = forms.IntegerField(
        min_value=1,
        required=False,
        label='First data row',
        help_text=('Select number of first row with data. The first row '
                   'has index 1'))

    #: Select column for lanes
    lane_numbers_column = forms.IntegerField(
        min_value=1,
        required=True,
        label='Lane column index',
        help_text='The first column has index 1')


class ConfirmExtractionForm(forms.Form):
    """Empty form, used for confirming that the detection worked correctly
    """
