from django.db import models
from django.core.exceptions import ValidationError

from markdown_deux.templatetags.markdown_deux_tags import markdown_allowed

# SequencingMachine and related ----------------------------------------------

#: Choices for machine models
MACHINE_MODELS = (
    ('MiSeq', 'MiSeq'),
    ('MiniSeq', 'MiniSeq'),
    ('NextSeq500', 'NextSeq 500'),
    ('HiSeq1000', 'HiSeq 1000'),
    ('HiSeq1500', 'HiSeq 1500'),
    ('HiSeq3000', 'HiSeq 3000'),
    ('HiSeq4000', 'HiSeq 4000'),
    ('other', 'Other'),  # be a bit more future proof
)


#: Choices for index workflows, determines whether the second index is read
#: as reverse-complement or not for dual indexing.  Could be inferred from
#: the machine type but not doing so as we would have to know all machine
#: types at any time.
INDEX_WORKFLOWS = (
    ('A', 'MiSeq, HiSeq <=2500'),
    ('B', 'MiniSeq, NextSeq, HiSeq >=3000'),
)


class SequencingMachine(models.Model):
    """Represent a sequencing machine instance
    """

    #: Timestamp for creation time
    created_at = models.DateTimeField(auto_now_add=True)
    #: Timestamp for last update
    updated_at = models.DateTimeField(auto_now=True)

    #: Vendor ID of the machine, reflected in file names and read names later
    #: on
    vendor_id = models.CharField(
        max_length=100,
        help_text='Vendor ID of the machine')

    #: Human-readable label of the machine
    label = models.CharField(
        max_length=100,
        help_text='Short name of the machine')

    #: Optional, short description of the machine
    description = models.TextField(
        blank=True,
        null=True,
        help_text=(
            'Short description regarding the machine' +
            markdown_allowed()))

    #: The machine model to use
    machine_model = models.CharField(
        choices=MACHINE_MODELS,
        max_length=100,
        help_text='The model of the machine')

    #: Number of slots in the machine
    slot_count = models.IntegerField(default=1)

    #: Workflow used for dual indexing
    dual_index_workflow = models.CharField(
        max_length=10,
        choices=INDEX_WORKFLOWS,
        default='A',
        help_text='Workflow to use for dual indexing')

    def __str__(self):
        tpl = 'SequencingMachine({})'
        vals = (self.vendor_id, self.label, self.description,
                self.machine_model, self.slot_count, self.dual_index_workflow)
        return tpl.format(', '.join(map(repr, vals)))

    def __repr__(self):
        return str(self)


# BarcodeSet and related -----------------------------------------------------


class BarcodeSet(models.Model):
    """A set of barcodes with id => sequence mapping"""

    #: Timestamp for creation time
    created_at = models.DateTimeField(auto_now_add=True)
    #: Timestamp for last update
    updated_at = models.DateTimeField(auto_now=True)

    #: Full name of the index set
    name = models.CharField(
        max_length=100,
        help_text='Full name of the barcode adapter set')

    #: Short, unique identifier of the barcode index set
    short_name = models.CharField(
        max_length=100, unique=True, db_index=True,
        help_text='Short, unique identifier of barcode adapter set')

    def __str__(self):
        return '{} ({})'.format(self.name, self.short_name)

    def __repr__(self):
        tpl = 'BarcodeSet({})'
        values = (self.name, self.short_name)
        return tpl.format(', '.join(map(repr, values)))


class BarcodeSetEntry(models.Model):
    """A barcode sequence with an id"""

    #: Timestamp for creation time
    created_at = models.DateTimeField(auto_now_add=True)
    #: Timestamp for last update
    updated_at = models.DateTimeField(auto_now=True)

    #: The barcode set that this barcode belongs to
    barcode_set = models.ForeignKey(BarcodeSet, related_name='barcodes',
                                    on_delete=models.CASCADE)

    #: The identifier of the adapter, e.g., 'AR001'.  This has to be unique
    #: in the context of the ``BarcodeSet``
    name = models.CharField(max_length=100, db_index=True, unique=False)

    #: DNA sequence of the barcode.  In the case of dual indexing, use the
    #: sequence as for workflow A
    sequence = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        """Version of save() that ensure uniqueness of the name within the
        BarcodeSet
        """
        self._validate_unique()
        super().save(*args, **kwargs)

    def _validate_unique(self):
        """Validates that the name and sequence are unique within the
        BarcodeSet
        """
        # check for unique name
        for key in ('name', 'sequence'):
            qs = BarcodeSetEntry.objects.filter(**{key: getattr(self, key)})
            if qs.filter(barcode_set=self.barcode_set).exists():
                raise ValidationError(
                    'Barcode {} must be unique in barcode set!'.format(key))

    def __str__(self):
        return '{} ({})'.format(self.name, self.sequence)

    def __repr__(self):
        tpl = 'BarcodeSetEntry({})'
        values = (self.name, self.sequence)
        return tpl.format(', '.join(map(repr, values)))
