# -*- coding: utf-8 -*-
"""Models for the flowcells app"""

from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
from django.contrib.contenttypes.fields import GenericRelation

import rules

from flowcelltool.users.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from model_utils.models import TimeStampedModel
from ..threads.models import Message

from markdown_deux.templatetags.markdown_deux_tags import markdown_allowed


# SequencingMachine and related ------------------------------------------

#: Key value for machine model MiSeq
MACHINE_MODEL_MISEQ = 'MiSeq'

#: Key value for machine model MiniSeq
MACHINE_MODEL_MINISEQ = 'MiniSeq'

#: Key value for machine model NextSeq500
MACHINE_MODEL_NEXTSEQ500 = 'NextSeq500'

#: Key value for machine model HiSeq1000
MACHINE_MODEL_HISEQ1000 = 'HiSeq1000'

#: Key value for machine model HiSeq1500
MACHINE_MODEL_HISEQ1500 = 'HiSeq1500'

#: Key value for machine model HiSeq2000
MACHINE_MODEL_HISEQ2000 = 'HiSeq2000'

#: Key value for machine model HiSeq3000
MACHINE_MODEL_HISEQ3000 = 'HiSeq3000'

#: Key value for machine model HiSeq4000
MACHINE_MODEL_HISEQ4000 = 'HiSeq4000'

#: Key value for 'other' machine models
MACHINE_MODEL_OTHER = 'other'

#: Choices for machine models
MACHINE_MODELS = (
    (MACHINE_MODEL_MISEQ, 'MiSeq'),
    (MACHINE_MODEL_MINISEQ, 'MiniSeq'),
    (MACHINE_MODEL_NEXTSEQ500, 'NextSeq 500'),
    (MACHINE_MODEL_HISEQ1000, 'HiSeq 1000'),
    (MACHINE_MODEL_HISEQ1500, 'HiSeq 1500'),
    (MACHINE_MODEL_HISEQ2000, 'HiSeq 2000'),
    (MACHINE_MODEL_HISEQ3000, 'HiSeq 3000'),
    (MACHINE_MODEL_HISEQ4000, 'HiSeq 4000'),
    (MACHINE_MODEL_OTHER, 'Other'),  # be a bit more future proof
)

#: Key value for index workflow A
INDEX_WORKFLOW_A = 'A'

#: Key value for index workflow B
INDEX_WORKFLOW_B = 'B'

#: Choices for index workflows, determines whether the second index is read
#: as reverse-complement or not for dual indexing.  Could be inferred from
#: the machine type but not doing so as we would have to know all machine
#: types at any time.
INDEX_WORKFLOWS = (
    (INDEX_WORKFLOW_A, 'MiSeq, HiSeq <=2500'),
    (INDEX_WORKFLOW_B, 'MiniSeq, NextSeq, HiSeq >=3000'),
)


class SequencingMachine(TimeStampedModel):
    """Represent a sequencing machine instance
    """

    #: Vendor ID of the machine, reflected in file names and read names later
    #: on
    vendor_id = models.CharField(
        unique=True, db_index=True,
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
            'Short description of the machine. ' +
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
        default=INDEX_WORKFLOW_A,
        help_text='Workflow to use for dual indexing')

    def get_absolute_url(self):
        return reverse('instrument_view', kwargs={'pk': self.pk})

    # Permissions -------------------------------------------------------------

    # The boilerplate below ("DRY permissions") hooks up the DRY REST permission system into our
    # django-rules based system.

    @staticmethod
    def has_None_permission(request):
        # TODO: why do we need this? Only for the automatically generated UI?
        return False

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    @staticmethod
    def has_list_permission(request):
        return request.user.has_perm('flowcells.list_sequencingmachine')

    @staticmethod
    def has_create_permission(request):
        return request.user.has_perm('flowcells.add_sequencingmachine')

    def has_object_retrieve_permission(self, request):
        return request.user.has_perm('flowcells.view_sequencingmachine', self)

    def has_object_update_permission(self, request):
        return request.user.has_perm('flowcells.change_sequencingmachine', self)

    def has_object_destroy_permission(self, request):
        return request.user.has_perm('flowcells.delete_sequencingmachine', self)

    # Boilerplate str/repr ----------------------------------------------------

    def __str__(self):
        tpl = 'SequencingMachine({})'
        vals = (self.vendor_id, self.label, self.description,
                self.machine_model, self.slot_count, self.dual_index_workflow)
        return tpl.format(', '.join(repr(v) for v in vals))

    def __repr__(self):
        return str(self)


# BarcodeSet and related -----------------------------------------------------


class BarcodeSet(TimeStampedModel):
    """A set of barcodes with id => sequence mapping"""

    #: Full name of the index set
    name = models.CharField(
        max_length=100,
        help_text='Full name of the barcode adapter set')

    #: Short, unique identifier of the barcode index set
    short_name = models.CharField(
        max_length=100, unique=True, db_index=True,
        help_text='Short, unique identifier of barcode adapter set')

    #: Optional, short description of the barcode set, including copyright
    #: notices etc.
    description = models.TextField(
        blank=True, null=True,
        help_text=('Short description of the barcode set. ' +
                   markdown_allowed()))

    @property
    def sorted_entries(self):
        """Return barcode set entries, sorted by name"""
        return self.entries.order_by('name')

    def get_absolute_url(self):
        return reverse('barcodeset_view', kwargs={'pk': self.pk})

    # Permissions -------------------------------------------------------------

    # The boilerplate below ("DRY permissions") hooks up the DRY REST permission system into our
    # django-rules based system.

    @staticmethod
    def has_None_permission(request):
        # TODO: why do we need this? Only for the automatically generated UI?
        return False

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    @staticmethod
    def has_list_permission(request):
        return request.user.has_perm('flowcells.list_barcodeset')

    @staticmethod
    def has_create_permission(request):
        return request.user.has_perm('flowcells.add_barcodeset')

    def has_object_retrieve_permission(self, request):
        return request.user.has_perm('flowcells.view_barcodeset', self)

    def has_object_update_permission(self, request):
        return request.user.has_perm('flowcells.change_barcodeset', self)

    def has_object_destroy_permission(self, request):
        return request.user.has_perm('flowcells.delete_barcodeset', self)

    # Boilerplate str/repr ----------------------------------------------------

    def __str__(self):
        return '{} ({})'.format(self.name, self.short_name)

    def __repr__(self):
        tpl = 'BarcodeSet({})'
        values = (self.name, self.short_name)
        return tpl.format(', '.join(repr(v) for v in values))


class BarcodeSetEntry(TimeStampedModel):
    """A barcode sequence with an id"""

    #: The barcode set that this barcode belongs to
    barcode_set = models.ForeignKey(BarcodeSet, related_name='entries',
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
            if self.pk is not None:
                qs = qs.exclude(pk=self.pk)
            if qs.filter(barcode_set=self.barcode_set).exists():
                raise ValidationError(
                    'Barcode {} must be unique in barcode set!'.format(key))

    # Permissions -------------------------------------------------------------

    # The boilerplate below ("DRY permissions") hooks up the DRY REST permission system into our
    # django-rules based system.

    @staticmethod
    def has_None_permission(request):
        # TODO: why do we need this? Only for the automatically generated UI?
        return False

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    @staticmethod
    def has_list_permission(request):
        return request.user.has_perm('flowcells.list_barcodesetentry')

    @staticmethod
    def has_create_permission(request):
        return request.user.has_perm('flowcells.add_barcodesetentry')

    def has_object_retrieve_permission(self, request):
        return request.user.has_perm('flowcells.view_barcodesetentry', self)

    def has_object_update_permission(self, request):
        return request.user.has_perm('flowcells.change_barcodesetentry', self)

    def has_object_destroy_permission(self, request):
        return request.user.has_perm('flowcells.delete_barcodesetentry', self)

    # Boilerplate str/repr ----------------------------------------------------

    def __str__(self):
        return '{} ({})'.format(self.name, self.sequence)

    def __repr__(self):
        tpl = 'BarcodeSetEntry({})'
        values = (self.name, self.sequence)
        return tpl.format(', '.join(repr(v) for v in values))


# FlowCell and related -------------------------------------------------------

#: Flow cell status key for initial state
FLOWCELL_STATUS_INITIAL = 'initial'

#: Flow cell status key for sequencing complete
FLOWCELL_STATUS_SEQ_COMPLETE = 'seq_complete'

#: Flow cell status key for sequencing failed
FLOWCELL_STATUS_SEQ_FAILED = 'seq_failed'

#: Flow cell status key for demultiplexing started
FLOWCELL_STATUS_DEMUX_STARTED = 'demux_started'

#: Flow cell status key for demultiplexing complete
FLOWCELL_STATUS_DEMUX_COMPLETE = 'demux_complete'

#: Flow cell status key for demultiplexing delivered
FLOWCELL_STATUS_DEMUX_DELIVERED = 'demux_delivered'

#: Flow cell status key for bcls delivered
FLOWCELL_STATUS_BCL_DELIVERED = 'bcl_delivered'

#: Flow cell status choices
FLOWCELL_STATUS_CHOICES = (
    #: initial, known to the system but no sequencing or demultiplexing
    #: happened yet
    (FLOWCELL_STATUS_INITIAL, 'initial'),
    #: sequencing complete, the files are completely written to the storage
    #: volume
    (FLOWCELL_STATUS_SEQ_COMPLETE, 'sequecing complete'),
    #: sequencing failed, possibly there are files but the sequencing has
    #: not succeeded
    (FLOWCELL_STATUS_SEQ_FAILED, 'sequencing failed'),
    #: demultiplexing has been completed
    (FLOWCELL_STATUS_DEMUX_COMPLETE, 'demultiplexing complete'),
    #: demultiplexing running, the demultiplexing operator started filling
    #: out the sample sheet in the flow cell tool and goes on running the
    #: demultiplexing
    (FLOWCELL_STATUS_DEMUX_STARTED, 'demultiplexing started'),
    #: demultiplexed files have been moved to their final destination, either
    #: in-house or to a customer/project partner, the raw base calls
    #: might also be delivered
    (FLOWCELL_STATUS_DEMUX_DELIVERED, 'demultiplexing results delivered'),
    #: raw BCL files have been delivered without demultiplexing as requested
    #: by the customer/project partner
    (FLOWCELL_STATUS_BCL_DELIVERED, 'base calls delivered'),
)


#: RTA version key for v1
RTA_VERSION_V1 = 1

#: RTA version key for v2
RTA_VERSION_V2 = 2

#: RTA version key for 'other'
RTA_VERSION_OTHER = 0

#: RTA version used for a flow cell
RTA_VERSION_CHOICES = (
    #: RTA v1.x, old bcl2fastq required
    (RTA_VERSION_V1, 'RTA v1'),
    #: RTA v2.x, bcl2fast2 required
    (RTA_VERSION_V2, 'RTA v2'),
    #: other, for future-proofness
    (RTA_VERSION_OTHER, 'other'),
)


class FlowCell(TimeStampedModel):
    """Information stored for each flow cell"""

    #: Owner of the flow cell.  Set to NULL when the user is deleted to
    #: circumvent any possible data loss.  Users should be deactivated
    #: instead of being deleted anyway
    owner = models.ForeignKey(User, null=True, blank=True,
                              on_delete=models.SET_NULL)

    #: Run date of the flow cell
    run_date = models.DateField()

    #: The sequencer used for processing this flow cell
    sequencing_machine = models.ForeignKey(
        SequencingMachine, null=True, blank=True, on_delete=models.SET_NULL)

    #: The run number on the machine
    run_number = models.PositiveIntegerField()

    #: The slot of the machine
    slot = models.CharField(max_length=1)

    #: The vendor ID of the flow cell name
    vendor_id = models.CharField(max_length=40)

    #: The label of the flow cell
    label = models.CharField(blank=True, null=True, max_length=100)

    #: Short description length
    description = models.TextField(
        blank=True,
        null=True,
        help_text=(
            'Short description of the flow cell ' +
            markdown_allowed()))

    #: Number of lanes on the flow cell
    num_lanes = models.IntegerField(
        default=8,
        help_text='Number of lanes on flowcell 8 for HiSeq, 4 for NextSeq')

    #: Status of the flow cell, as tracked with this app
    status = models.CharField(
        max_length=50, default=FLOWCELL_STATUS_INITIAL,
        choices=FLOWCELL_STATUS_CHOICES,
        help_text='Processing status of flow cell')

    #: Name of the sequencing machine operator
    operator = models.CharField(
        max_length=100, verbose_name='Sequencer Operator')

    #: The user responsible for demultiplexing
    demux_operator = models.ForeignKey(
        User, verbose_name='Demultiplexing Operator',
        related_name='demuxed_flowcells', on_delete=models.SET_NULL,
        null=True, blank=True, help_text='User responsible for demultiplexing')

    #: Whether or not the run was executed in a paired-end fashion
    is_paired = models.BooleanField(
        default=False, help_text='Check for paired reads')

    #: Number of index reads used.
    index_read_count = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(2)],
        default=1, help_text='Number of index reads that were used (0..2)')

    #: RTA version used, required for picking BCL to FASTQ and demultiplexing
    #: software
    rta_version = models.IntegerField(
        default=RTA_VERSION_V2, choices=RTA_VERSION_CHOICES,
        help_text='Major RTA version, implies bcl2fastq version')

    #: Read length that was configured
    read_length = models.IntegerField(default=151)

    #: Messages attached to this flowcell
    messages = GenericRelation(
        Message, content_type_field='content_type',
        object_id_field='object_id')

    def get_full_name(self):
        """Return full flow cell name"""
        if all(not x for x in (self.run_date, self.sequencing_machine,
                               self.run_number, self.slot, self.vendor_id,
                               self.label)):
            return ''
        else:
            return '_'.join(map(str, [x for x in [
                '' if not self.run_date else self.run_date.strftime('%y%m%d'),
                ('' if not self.sequencing_machine
                 else self.sequencing_machine.vendor_id),
                '{:04}'.format(0 if not self.run_number else self.run_number),
                self.slot,
                self.vendor_id,
                self.label
            ] if x]))

    def get_lanes(self):
        """Return a list of Library lists, for the layout on the flow cell"""
        try:
            lanes = [[] for i in range(self.num_lanes)]
            for lib in self.libraries.order_by('name'):
                for lane in lib.lane_numbers:
                    lanes[lane - 1].append(lib)
            return lanes
        except IndexError:
            return '(invalid)'

    @property
    def sorted_libraries(self):
        """Return libraries entries, sorted by name"""
        return self.libraries.order_by('name')

    def save(self, *args, **kwargs):
        self._validate_num_lanes()
        super().save(*args, **kwargs)

    def _validate_num_lanes(self):
        """Check that the num_lanes value is compatible with any contained
        Library
        """
        for library in self.libraries.all():
            if any(l > self.num_lanes for l in library.lane_numbers):
                raise ValidationError(
                    'Library {} is on lane [{}] (> {})'.format(
                        library.name, list(sorted(library.lane_numbers)),
                        self.num_lanes))


    def count_files(self):
        """Return total number of attached files"""
        result = 0
        for message in self.messages.all():  # pylint:disable=no-member
            result += message.attachments.all().count()
        return result

    def get_absolute_url(self):
        return reverse('flowcell_view', kwargs={'pk': self.pk})

    # Permissions -------------------------------------------------------------

    # The boilerplate below ("DRY permissions") hooks up the DRY REST permission system into our
    # django-rules based system.

    @staticmethod
    def has_None_permission(request):
        # TODO: why do we need this? Only for the automatically generated UI?
        return False

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    @staticmethod
    def has_list_permission(request):
        return request.user.has_perm('flowcells.list_flowcell')

    @staticmethod
    def has_create_permission(request):
        return request.user.has_perm('flowcells.add_flowcell')

    def has_object_retrieve_permission(self, request):
        return request.user.has_perm('flowcells.view_flowcell', self)

    def has_object_sample_sheet_permission(self, request):
        """Special action for building sample sheet, same as retrieve."""
        return self.has_object_retrieve_permission(request)

    def has_object_by_vendor_id_permission(self, request):
        """Special action for querying by vendor id, same as retrieve."""
        return self.has_object_retrieve_permission(request)

    def has_object_update_permission(self, request):
        return request.user.has_perm('flowcells.change_flowcell', self)

    def has_object_destroy_permission(self, request):
        return request.user.has_perm('flowcells.delete_flowcell', self)

    # Boilerplate str/repr ----------------------------------------------------

    def __str__(self):
        return str(self.get_full_name())

    def __repr__(self):
        tpl = 'FlowCell({})'
        values = (self.run_date, self.sequencing_machine, self.run_number,
                  self.slot, self.vendor_id, self.label, self.num_lanes,
                  self.status, self.operator, self.is_paired,
                  self.index_read_count, self.rta_version, self.read_length)
        return tpl.format(', '.join(repr(v) for v in values))


#: Reference used for identifying human samples
REFERENCE_HUMAN = 'hg19'

#: Reference used for identifying mouse samples
REFERENCE_MOUSE = 'mm9'

#: Reference used for identifying fly samples
REFERENCE_FLY = 'dm6'

#: Reference used for identifying fish samples
REFERENCE_FISH = 'danRer6'

#: Reference used for identifying rat samples
REFERENCE_RAT = 'rn11'

#: Reference used for identifying worm samples
REFERENCE_WORM = 'ce11'

#: Reference used for identifying yeast samples
REFERENCE_YEAST = 'sacCer3'

#: Reference used for identifying other samples
REFERENCE_OTHER = '__other__'

#: Reference sequence choices, to identify organisms
REFERENCE_CHOICES = (
    #: H. sapiens
    (REFERENCE_HUMAN, 'human'),
    #: M. musculus
    (REFERENCE_MOUSE, 'mouse'),
    #: D. melanogaster
    (REFERENCE_FLY, 'fly'),
    #: D. rerio
    (REFERENCE_FISH, 'zebrafish'),
    #: R. norvegicus
    (REFERENCE_RAT, 'rat'),
    #: C. elegans
    (REFERENCE_WORM, 'worm'),
    #: S. cerevisae
    (REFERENCE_YEAST, 'yeast'),
    #: other
    (REFERENCE_OTHER, 'other'),
)


def try_helper(f, arg, exc=AttributeError, default=''):
    """Helper for easy nullable access"""
    try:
        return f(arg)
    except exc:
        return default


class Library(TimeStampedModel):
    """The data stored for each library that is to be sequenced
    """

    class Meta:
        ordering = ['name']

    #: The flow cell that this library has been sequenced on
    flow_cell = models.ForeignKey(FlowCell, related_name='libraries',
                                  on_delete=models.CASCADE)

    #: The name of the library
    name = models.CharField(max_length=100)

    #: The organism to assume for this library, used for QC
    reference = models.CharField(
        max_length=100, default='hg19', choices=REFERENCE_CHOICES)

    #: The barcode set used for first barcode index of this library
    barcode_set = models.ForeignKey(
        BarcodeSet, null=True, blank=True, on_delete=models.SET_NULL)

    #: The barcode used for first barcode index this library
    barcode = models.ForeignKey(
        BarcodeSetEntry, null=True, blank=True, on_delete=models.SET_NULL)

    #: The barcode set used for second barcode index of this library
    barcode_set2 = models.ForeignKey(
        BarcodeSet, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='barcode_sets2')

    #: The barcode used for second barcode index this library
    barcode2 = models.ForeignKey(
        BarcodeSetEntry, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='barcodes2')

    #: The lanes that the library was sequenced on on the flow cell
    lane_numbers = ArrayField(
        models.IntegerField(validators=[MinValueValidator(1)]))

    def save(self, *args, **kwargs):
        """ Override to check name/barcode being unique on the flow cell
        lanes and lane numbers are compatible
        """
        self._validate_uniqueness()
        self._validate_lane_nos()
        return super().save(*args, **kwargs)

    def _validate_lane_nos(self):
        if any(l > self.flow_cell.num_lanes for l in self.lane_numbers):
            raise ValidationError(
                'Lane no {} > flow cell lane count {}'.format(
                    list(sorted(self.lane_numbers)),
                    self.flow_cell.num_lanes))

    def _validate_uniqueness(self):
        # Get all libraries sharing any lane on the same flow cell
        libs_on_lanes = Library.objects.filter(
            flow_cell=self.flow_cell,
            lane_numbers__overlap=self.lane_numbers
        ).exclude(
            pk=self.pk
        )
        # Check that no libraries exist with the same
        if libs_on_lanes.filter(name=self.name).exists():
            raise ValidationError(
                ('There are libraries sharing flow cell lane with the '
                 'same name as {}'.format(self.name)))
        # Check that no libraries exist with the same primary and secondary
        # barcode
        kwargs = {}
        if self.barcode is None:
            kwargs['barcode__isnull'] = True
        else:
            kwargs['barcode'] = self.barcode
        if self.barcode2 is None:
            kwargs['barcode2__isnull'] = True
        else:
            kwargs['barcode2'] = self.barcode2
        if libs_on_lanes.filter(**kwargs).exists():
            raise ValidationError(
                ('There are libraries sharing flow cell lane with the '
                 'same barcodes as {}: {}/{}'.format(
                     self.name, self.barcode, self.barcode2)))

    def get_absolute_url(self):
        return self.flow_cell.get_absolute_url()

    def get_search_result(self):
        return {
            'type': 'Library',
            'title': self.name,
            'description': 'on flow cell {}'.format(
                self.flow_cell.vendor_id)
        }

    # Permissions -------------------------------------------------------------

    # The boilerplate below ("DRY permissions") hooks up the DRY REST permission system into our
    # django-rules based system.

    @staticmethod
    def has_None_permission(request):
        # TODO: why do we need this? Only for the automatically generated UI?
        return False

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    @staticmethod
    def has_list_permission(request):
        return request.user.has_perm('flowcells.list_library')

    @staticmethod
    def has_create_permission(request):
        return request.user.has_perm('flowcells.add_library')

    def has_object_retrieve_permission(self, request):
        return request.user.has_perm('flowcells.view_library', self)

    def has_object_update_permission(self, request):
        return request.user.has_perm('flowcells.change_library', self)

    def has_object_destroy_permission(self, request):
        return request.user.has_perm('flowcells.delete_library', self)

    # Boilerplate str/repr ----------------------------------------------------

    def __str__(self):
        values = (
            self.name,
            try_helper(lambda b: b.name, self.barcode),
            try_helper(lambda b: b.sequence, self.barcode),
            try_helper(lambda b: b.name, self.barcode2),
            try_helper(lambda b: b.sequence, self.barcode2))
        return '{} ({}:{}, {}:{})'.format(*map(str, values))  # noqa

    def __repr__(self):
        tpl = 'Library({})'
        values = (self.flow_cell.get_full_name(), self.reference,
                  self.barcode_set, self.barcode, self.lane_numbers)
        return tpl.format(', '.join(map(repr, values)))  # noqa
