import uuid

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from db_file_storage.model_utils import delete_file, delete_file_if_needed
from model_utils.models import TimeStampedModel

from django.conf import settings

# Mixin for UUID ---------------------------------------------------------


class UuidStampedMixin(models.Model):
    """Mixin for "uuid" field."""

    uuid = models.UUIDField(
        default=uuid.uuid4,
        null=False,
        blank=False,
        editable=False,
        unique=True
    )

    class Meta:
        abstract = True


# Message and related ---------------------------------------------------------

#: MIME type for Markdown
MARKDOWN = 'text/markdown'
#: MIME type for plain text
PLAIN_TEXT = 'text/plain'
#: Choices for Message formats
FORMAT_CHOICES = (
    (MARKDOWN, 'Markdown'),
    (PLAIN_TEXT, 'Plain Text'),
)


class Message(UuidStampedMixin, TimeStampedModel):
    """A message that is written by a user"""

    # Messages related to a "thread" items on
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    thread_object = GenericForeignKey('content_type', 'object_id')

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    title = models.CharField(
        blank=True, null=True, max_length=200,
        help_text='Optional title for the message')
    body = models.TextField(blank=True, null=True, help_text='Your message')

    mime_type = models.CharField(max_length=50, default='text/plain',
                                 choices=FORMAT_CHOICES)

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
        return request.user.has_perm('threads.list_message')

    @staticmethod
    def has_create_permission(request):
        return request.user.has_perm('threads.add_message')

    def has_object_retrieve_permission(self, request):
        return request.user.has_perm('threads.view_message', self)

    def has_object_update_permission(self, request):
        return request.user.has_perm('threads.change_message', self)

    def has_object_destroy_permission(self, request):
        return request.user.has_perm('threads.delete_message', self)

    # Boilerplate str/repr ----------------------------------------------------

    def __str__(self):
        return 'Message({}, {}, {})'.format(self.title, self.author.username,
                                            self.body)


# Attachment ------------------------------------------------------------------


class AttachmentFile(UuidStampedMixin, TimeStampedModel):

    bytes = models.TextField()
    filename = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=255)


class Attachment(UuidStampedMixin, TimeStampedModel):
    message = models.ForeignKey(Message, related_name='attachments', on_delete=models.CASCADE)
    payload = models.FileField(
        upload_to='threads.AttachmentFile/bytes/filename/mimetype')

    def save(self, *args, **kwargs):
        delete_file_if_needed(self, 'payload')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        delete_file(self, 'payload')
