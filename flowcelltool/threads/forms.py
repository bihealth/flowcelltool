# -*- coding: utf-8 -*-
from django import forms
from django.db import transaction
from django.contrib.contenttypes.models import ContentType

from multiupload.fields import MultiFileField

from . import models


class MessageForm(forms.ModelForm):
    attachments = MultiFileField(min_num=0, max_num=20,
                                 max_file_size=1024 * 1024 * 5,
                                 required=False)

    class Meta:
        model = models.Message
        fields = ['title', 'body', 'attachments']

    def save(self, request, related_obj, *args, **kwargs):
        with transaction.atomic():
            self.instance.author = request.user
            self.instance.content_type = ContentType.objects.get_for_model(
                related_obj)
            self.instance.object_id = related_obj.pk
            self.instance.save()
            for attachment in self.cleaned_data['attachments']:
                self.instance.attachments.create(payload=attachment)
            super().save(*args, **kwargs)
