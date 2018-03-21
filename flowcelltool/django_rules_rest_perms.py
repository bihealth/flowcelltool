# -*- coding: utf-8 -*-
"""Integration of ``django-rules`` rules into the ``django-rest-framework``
permission framework.

We found all other solutions lacking or too verbose, thus the simple integration.

------------
Installation
------------

Simply add the class ``DjangoRulesPermission`` to your configuration::

    REST_FRAMEWORK = {
        # ...
        'DEFAULT_PERMISSION_CLASSES': (
            'flowcelltool.flowcells.django_rules_rest_perms.DjangoRulesPermission',
        ),
        # ...
    }

-----------
Rule Naming
-----------

Using the "convention over configuration" paradigm, your rules should have the
following structure::

    ``app[.ModelName]:action``

The ``app`` is the name of your Django app that hosts the ``model`` module.  The ``model``
is the class name of the model to protect and the ``action`` is one of the default actions
from Django Rest Framework:

- ``access``
- ``list``
- ``retrieve``
- ``update``
- ``partial_update``
- ``destroy``

When ``partial_update`` is not specified, ``update`` will be used.

For each action, the following checks are performed:

1. The ``app:access`` rule must return ``True`` for the user.
2. For the standard actions, ``app.Model:action`` must be ``True`` for the user.  In case
   of ``app.Model:partial_update`` not being defined, ``app.Model:update`` will be used
   instead
3. For any other action, ``app.Model:action`` must return true.

Note that for all but ``list``, the object-level permissions will be used.

---
API
---

The following public classes are available:

- ``DjangoRulesPermission`` can be used in the global configuration.
- ``rule_or_permission_denied(rule, user[, object[, msg]])`` will throw
  ``PermissionDenied`` if the rule is not ``True`` for the given user and object.
- ``@require_rule(rules=[], override_default=False)`` can be used as a decorator for
   your action to check whether the given rule is required.
- Define ``required_rule`` in your DRF CBV to check the rule.
"""

import functools

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


class DjangoRulesPermission(BasePermission):
    """Grant permissions based on rules from ``django-rules`` library.
    """

    def has_permission(self, request, view):
        """Return ``True`` if permission is granted, ``False`` otherwise."""
        import sys; print(request, view, file=sys.stderr)
        return True

    def has_object_permission(self, request, view, obj):
        """Return ``True`` if permission is granted, ``False`` otherwise."""
        import sys; print(request, view, file=sys.stderr)
        return True


def rule_or_permission_denied(rule_or_rules, user, obj=None, msg=None):
    if isinstance(rule_or_rules, str):
        rules = [rule_or_rules]
    else:
        rules = list(rule_or_rules or [])
    if not user.has_perms(rules, obj):
        msg = msg or "Insufficient permissions or rule mismatch!"
        raise PermissionDenied(msg)


def require_rule(rule_or_rules=None, override_default=False, msg=None):
    """Decorator for DRF ViewSets."""
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            assert False, 'TODO: check permissions here'
            return func(*args, **kwargs)
        return wrapper
    if isinstance(rule_or_rules, str):
        rules = [rule_or_rules]
    else:
        rules = list(rule_or_rules or [])
    actual_decorator.override_default = override_default
    return actual_decorator
