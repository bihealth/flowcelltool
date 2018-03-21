# -*- coding: utf-8 -*-
import rules

GUEST = 'Guest'
INSTRUMENT_OPERATOR = 'Instrument Operator'
DEMUX_OPERATOR = 'Demultiplexing Operator'
DEMUX_ADMIN = 'Demultiplexing Admin'
IMPORT_BOT = 'Import Bot'

# Predicates -------------------------------------------------------------


@rules.predicate
def is_flow_cell_owner(user, flow_cell):
    """Whether or not user is owner of the given flow cell"""
    if not flow_cell:
        return False
    else:
        return flow_cell.owner == user


@rules.predicate
def is_librarys_flow_cell_owner(user, library):
    """Whether or not is owner of the given flow cell's library'"""
    if not library or not library.flow_cell:
        return False
    else:
        return library.flow_cell.owner == user


@rules.predicate
def is_message_author(user, message):
    """Whether or not the user created the message"""
    if not message or not message.author:
        return False
    else:
        return message.author == user


@rules.predicate
def is_attachment_message_author(user, att):
    """Whether or not the user created the attachment's message"""
    if not att or not att.message or not att.message.author:
        return False
    else:
        return att.message.author == user


#: Whether or not has the "guest" group
is_guest = rules.is_group_member(GUEST)

#: Whether or not has the "Instrument Operator" group
is_instrument_operator = rules.is_group_member(INSTRUMENT_OPERATOR)

#: Whether or not has the "Demultiplexing Operator" group
is_demux_operator = rules.is_group_member(DEMUX_OPERATOR)

#: Whether or not has the "Demultiplexing Admin" group
is_demux_admin = rules.is_group_member(DEMUX_ADMIN)

#: Whether or not has the "Import Bot" group
is_import_bot = rules.is_group_member(IMPORT_BOT)


# Permissions ------------------------------------------------------------

# Allow everyone access to flowcells app
rules.add_perm('flowcells', rules.always_allow)

# Viewing and listing sequencing machines requires at least the guest group
rules.add_perm('flowcells.SequencingMachine:list',
               is_guest | is_instrument_operator | is_demux_operator |
               is_demux_admin | is_import_bot)
rules.add_perm('flowcells.SequencingMachine:retrieve',
               is_guest | is_instrument_operator | is_demux_operator |
               is_demux_admin | is_import_bot)
rules.add_perm('flowcells.SequencingMachine:by_vendor_id',
               is_guest | is_instrument_operator | is_demux_operator |
               is_demux_admin | is_import_bot | rules.is_superuser)

# Adding and updating sequencing machines requires to be a demultiplexing
# administrator as this can be very destructive
rules.add_perm('flowcells.SequencingMachine:create',
               is_demux_admin | rules.is_superuser)
rules.add_perm('flowcells.SequencingMachine:update',
               is_demux_admin | rules.is_superuser)
rules.add_perm('flowcells.SequencingMachine:destroy',
               is_demux_admin | rules.is_superuser)

# Viewing and listing barcode sets requires at least the guest group
rules.add_perm('flowcells.BarcodeSet:list',
               is_guest | is_instrument_operator | is_demux_operator |
               is_demux_admin | is_import_bot)
rules.add_perm('flowcells.BarcodeSet:retrieve',
               is_guest | is_instrument_operator | is_demux_operator |
               is_demux_admin | is_import_bot)

# Adding and updating barcode sets requires to be a demultiplexing
# administrator as this can be very destructive
rules.add_perm('flowcells.BarcodeSet:create',
               is_demux_admin | rules.is_superuser)
rules.add_perm('flowcells.BarcodeSet:update',
               is_demux_admin | rules.is_superuser)
rules.add_perm('flowcells.BarcodeSet:destroy',
               is_demux_admin | rules.is_superuser)

# Adding and updating barcode set entries requires to be a demultiplexing
# administrator as this can be very destructive
rules.add_perm('flowcells.BarcodeSetEntry:create',
               is_demux_admin | rules.is_superuser)
rules.add_perm('flowcells.BarcodeSetEntry:update',
               is_demux_admin | rules.is_superuser)
rules.add_perm('flowcells.BarcodeSetEntry:destroy',
               is_demux_admin | rules.is_superuser)

# Viewing and listing flow cells requires at least the guest group
rules.add_perm('flowcells.FlowCell:list',
               is_guest | is_instrument_operator | is_demux_operator |
               is_demux_admin | is_import_bot | rules.is_superuser)
rules.add_perm('flowcells.FlowCell:retrieve',
               is_guest | is_instrument_operator | is_demux_operator |
               is_demux_admin | is_import_bot | rules.is_superuser)
rules.add_perm('flowcells.FlowCell:by_vendor_id',
               is_guest | is_instrument_operator | is_demux_operator |
               is_demux_admin | is_import_bot | rules.is_superuser)
rules.add_perm('flowcells.FlowCell:sample_sheet',
               is_guest | is_instrument_operator | is_demux_operator |
               is_demux_admin | is_import_bot | rules.is_superuser)

# Adding flow cells can be done by everyone, updating is only possible to
# owners, demux operators and upwards.
rules.add_perm(
    'flowcells.FlowCell:create',
    is_instrument_operator | is_demux_operator | is_demux_admin |
    is_import_bot | rules.is_superuser
)
rules.add_perm(
    'flowcells.FlowCell:update',
    is_flow_cell_owner | is_demux_operator | is_demux_admin |
    rules.is_superuser
)
rules.add_perm(
    'flowcells.FlowCell:destroy',
    is_flow_cell_owner | is_demux_operator | is_demux_admin |
    rules.is_superuser
)


# Similar, for library on flowcell
rules.add_perm('flowcells.Library:list',
               is_guest | is_instrument_operator | is_demux_operator |
               is_demux_admin | is_import_bot | rules.is_superuser)
rules.add_perm('flowcells.Library:retrieve',
               is_guest | is_instrument_operator | is_demux_operator |
               is_demux_admin | is_import_bot | rules.is_superuser)

rules.add_perm(
    'flowcells.Library:create',
    is_librarys_flow_cell_owner | is_demux_operator | is_demux_admin |
    is_import_bot | rules.is_superuser
)
rules.add_perm(
    'flowcells.Library:update',
    is_librarys_flow_cell_owner | is_demux_operator | is_demux_admin |
    is_import_bot | rules.is_superuser
)
rules.add_perm(
    'flowcells.Library:destroy',
    is_librarys_flow_cell_owner | is_demux_admin |
    is_import_bot | rules.is_superuser
)

# Viewing and listing messages requires at least the guest group
rules.add_perm('flowcells.Message:list',
               is_guest | is_instrument_operator | is_demux_operator |
               is_demux_admin | is_import_bot | rules.is_superuser)
rules.add_perm('flowcells.Message:retrieve',
               is_guest | is_instrument_operator | is_demux_operator |
               is_demux_admin | is_import_bot | rules.is_superuser)

# Attaching messages to flow cells and modifying messages
rules.add_perm(
    'threads.Message:create',
    is_instrument_operator | is_demux_operator | is_demux_admin |
    is_import_bot | rules.is_superuser
)
rules.add_perm(
    'threads.Message:update',
    is_message_author | is_demux_admin | rules.is_superuser
)
rules.add_perm(
    'threads.Message:destroy',
    is_message_author | is_demux_admin | rules.is_superuser
)

# Attaching files to messages to flow cells and modifying messages
rules.add_perm(
    'threads.Attachment:create',
    is_instrument_operator | is_demux_operator | is_demux_admin |
    is_import_bot | rules.is_superuser
)
rules.add_perm(
    'threads.Attachment:update',
    is_attachment_message_author | is_demux_admin | rules.is_superuser
)
rules.add_perm(
    'threads.Attachment:destroy',
    is_attachment_message_author | is_demux_admin | rules.is_superuser
)

# Searching requires at least the guest role

rules.add_perm('flowcells:search',
               is_guest | is_instrument_operator | is_demux_operator |
               is_demux_admin | is_import_bot | rules.is_superuser)
