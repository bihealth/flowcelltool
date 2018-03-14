from django import template

import flowcelltool

register = template.Library()

@register.simple_tag(name='app_version')
def app_version():
    return flowcelltool.__version__
