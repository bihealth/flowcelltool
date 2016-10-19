from django.utils import six
from django.forms import CharField
from django.contrib.postgres.forms import SimpleArrayField
from django.contrib.postgres.validators import (
    ArrayMaxLengthValidator, ArrayMinLengthValidator,
)

from pagerange import PageRange


class IntegerRangeField(CharField):
    """Custom widget for entering integer as ranges

    E.g., the following are valid:

    - "1,2"
    - "1-3,4,5"
    """

    def __init__(self, max_length=None, min_length=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial = []
        if min_length is not None:
            self.min_length = min_length
            self.validators.append(ArrayMinLengthValidator(int(min_length)))
        if max_length is not None:
            self.max_length = max_length
            self.validators.append(ArrayMaxLengthValidator(int(max_length)))

    def prepare_value(self, value):
        if isinstance(value, list):
            value = PageRange(value).range
        return value

    def to_python(self, value):
        if value:
            items = PageRange(value).pages
        else:
            items = []
        return items

    def clean(self, value):
        value = self.to_python(value)
        self.validate(value)
        self.run_validators(value)
        return value
