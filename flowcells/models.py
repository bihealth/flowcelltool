from django.db import models

from markdown_deux.templatetags.markdown_deux_tags import markdown_allowed


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
