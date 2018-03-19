# -*- coding: utf-8 -*-

from django import forms

from crispy_forms.helper import FormHelper


class UserTokenCreateForm(forms.Form):
    """This form allows token creation"""

    #: Time to live in hours
    ttl = forms.IntegerField(
        label='Time to live', min_value=0, required=True, initial=0,
        help_text='Time to live in hours, set to 0 for tokens that never expire.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.template_pack = 'bootstrap4'
        self.helper.form_tag = False
