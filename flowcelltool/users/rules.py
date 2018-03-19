# -*- coding: utf-8 -*-
import rules

# Predicates -------------------------------------------------------------


@rules.predicate
def is_token_owner(user, token):
    """Whether or not user is owner of the given flow cell"""
    if not token:
        return False
    else:
        return token.user == user


# Permissions ------------------------------------------------------------

# Allow everyone access to flowcells app
rules.add_perm('users.delete_token', is_token_owner)
