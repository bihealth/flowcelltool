import os

from django import template

import flowcelltool

register = template.Library()


@register.simple_tag(name='app_version')
def app_version():
    return flowcelltool.__version__


@register.simple_tag
def getenv(name, empty=''):
    return os.environ.get(name, empty)
