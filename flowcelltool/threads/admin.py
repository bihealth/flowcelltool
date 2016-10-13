# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline

from .models import Message


class MessageInlines(GenericStackedInline):
    model = Message
    exclude = ()


extra = 1
