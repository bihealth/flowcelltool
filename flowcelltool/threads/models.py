from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from db_file_storage.model_utils import delete_file, delete_file_if_needed

from django.conf import settings


# TimeStampedModel ------------------------------------------------------------


class TimeStampedModel(models.Model):
    """Base class that adds the created_ad and updated_add field"""

    #: Timestamp for creation time
    created_at = models.DateTimeField(auto_now_add=True)
    #: Timestamp for last update
    updated_at = models.DateTimeField(auto_now=True)


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


class Message(TimeStampedModel):
    """A message that is written by a user"""

    # Messages related to a "thread" items on
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    author = models.ForeignKey(settings.AUTH_USER_MODEL)

    title = models.CharField(
        blank=True, null=True, max_length=200,
        help_text='Optional title for the message')
    body = models.TextField(blank=True, null=True, help_text='Your message')

    mime_type = models.CharField(max_length=50, default='text/plain',
                                 choices=FORMAT_CHOICES)

    def __str__(self):
        return 'Message({}, {}, {})'.format(self.title, self.author.username,
                                            self.body)


# Attachment ------------------------------------------------------------------


class AttachmentFile(TimeStampedModel):

    bytes = models.TextField()
    filename = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=255)


class Attachment(TimeStampedModel):
    message = models.ForeignKey(Message, related_name='attachments')
    payload = models.FileField(
        upload_to='threads.AttachmentFile/bytes/filename/mimetype')

    def save(self, *args, **kwargs):
        delete_file_if_needed(self, 'payload')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        delete_file(self, 'payload')
