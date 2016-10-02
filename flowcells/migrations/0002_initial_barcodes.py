# -*- coding: utf-8 -*-
"""Import initial barcode sets

- Illumina TruSeq Stranded mRNA LT Sample Prep Kit Set A
- Illumina TruSeq Stranded mRNA LT Sample Prep Kit Set B
- Agilent SureSelect XT
"""

import os
import csv
import textwrap

from django.db import migrations


def read_tsvs():
    """Read corresponding TSV file bundled with this migration
    """
    result = []
    path = os.path.join(os.path.dirname(__file__),
                        '0002_initial_barcodes.tsv')
    with open(path, 'rt') as f:
        tsvin = csv.reader(f, delimiter='\t')
        header = None
        for row in tsvin:
            if not header:
                header = row
            else:
                result.append(dict(zip(header, row)))
    return result


#: Data from the adapter TSV file
DATA = read_tsvs()

#: Illumina mRNA adapters set A
KEY_TRUSEQ_A = 'Illumina TruSeq Stranded mRNA LT Sample Prep Kit Set A'

#: Illumina mRNA adapters set B
KEY_TRUSEQ_B = 'Illumina TruSeq Stranded mRNA LT Sample Prep Kit Set B'

#: Agilent SureSelect XT adapters
KEY_SURE_SELECT = 'Agilent SureSelect XT'


def add_barcode_set(apps, schema_editor, data, data_keys, name, short_name,
                    description):
    """Generic function for adding a barcode set"""
    BarcodeSet = apps.get_model('flowcells', 'BarcodeSet')
    BarcodeSetEntry = apps.get_model('flowcells', 'BarcodeSetEntry')
    bs = BarcodeSet(name=name, short_name=short_name, description=description)
    bs.save()
    for row in data:
        if row['adapter_set'] not in data_keys:
            continue
        bs.barcodes.create(name=row['adapter_name'],
                           sequence=row['adapter_sequence'])


def remove_barcode_set(apps, schema_editor, short_name):
    """Generic function for removing a barcode set by short name"""
    BarcodeSet = apps.get_model('flowcells', 'BarcodeSet')
    for bs in BarcodeSet.objects.filter(short_name=short_name).all():
        bs.delete()


def add_agilent_sure_select_xt(apps, schema_editor):
    NAME = 'Agilent SureSelect XT'
    SHORT_NAME = 'SureSelect'
    DESCRIPTION = textwrap.dedent(r"""
        Index barcode for the Agilent SureSelect XT kit.

        All trademarks or copyrights are those of Agilent Inc.

        The sequences here are used in the hope that they are useful, no
        warranty of any kind is implied.
        """).strip()
    add_barcode_set(apps, schema_editor, DATA, (KEY_SURE_SELECT,),
                    NAME, SHORT_NAME, DESCRIPTION)


def remove_agilent_sure_select_xt(apps, schema_editor):
    SHORT_NAME = 'SureSelect'
    remove_barcode_set(apps, schema_editor, SHORT_NAME)


def add_illumina_truseq_stranded_mrna_both(apps, schema_editor):
    NAME = 'Illumina TruSeq Stranded mRNA LT Sample Prep Kit Set A+B'
    SHORT_NAME = 'TSMRAB'
    DESCRIPTION = textwrap.dedent(r"""
        Index barcode for the Illumina TruSeq Stranded mRNA LT Sample Prep
        Kit Set A+B.

        All trademarks or copyrights are those of Illumina, Inc.

        The sequences here are used in the hope that they are useful, no
        warranty of any kind is implied.
        """).strip()
    add_barcode_set(apps, schema_editor, DATA,
                    (KEY_TRUSEQ_A, KEY_TRUSEQ_B),
                    NAME, SHORT_NAME, DESCRIPTION)


def remove_illumina_truseq_stranded_mrna_both(apps, schema_editor):
    SHORT_NAME = 'TSMRAB'
    remove_barcode_set(apps, schema_editor, SHORT_NAME)


def add_illumina_truseq_stranded_mrna_set_a(apps, schema_editor):
    NAME = 'Illumina TruSeq Stranded mRNA LT Sample Prep Kit Set A+B'
    SHORT_NAME = 'TSMRA'
    DESCRIPTION = textwrap.dedent(r"""
        Index barcode for the Illumina TruSeq Stranded mRNA LT Sample Prep
        Kit Set A.

        All trademarks or copyrights are those of Illumina, Inc.

        The sequences here are used in the hope that they are useful, no
        warranty of any kind is implied.
        """).strip()
    add_barcode_set(apps, schema_editor, DATA,
                    (KEY_TRUSEQ_A,),
                    NAME, SHORT_NAME, DESCRIPTION)


def remove_illumina_truseq_stranded_mrna_set_a(apps, schema_editor):
    SHORT_NAME = 'TSMRA'
    remove_barcode_set(apps, schema_editor, SHORT_NAME)


def add_illumina_truseq_stranded_mrna_set_b(apps, schema_editor):
    NAME = 'Illumina TruSeq Stranded mRNA LT Sample Prep Kit Set A+B'
    SHORT_NAME = 'TSMRB'
    DESCRIPTION = textwrap.dedent(r"""
        Index barcode for the Illumina TruSeq Stranded mRNA LT Sample Prep
        Kit Set B.

        All trademarks or copyrights are those of Illumina, Inc.

        The sequences here are used in the hope that they are useful, no
        warranty of any kind is implied.
        """).strip()
    add_barcode_set(apps, schema_editor, DATA,
                    (KEY_TRUSEQ_B,),
                    NAME, SHORT_NAME, DESCRIPTION)


def remove_illumina_truseq_stranded_mrna_set_b(apps, schema_editor):
    SHORT_NAME = 'TSMRB'
    remove_barcode_set(apps, schema_editor, SHORT_NAME)


class Migration(migrations.Migration):

    dependencies = [
        ('flowcells', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_agilent_sure_select_xt,
                             remove_agilent_sure_select_xt),
        migrations.RunPython(add_illumina_truseq_stranded_mrna_both,
                             remove_illumina_truseq_stranded_mrna_both),
        migrations.RunPython(add_illumina_truseq_stranded_mrna_set_a,
                             remove_illumina_truseq_stranded_mrna_set_a),
        migrations.RunPython(add_illumina_truseq_stranded_mrna_set_b,
                             remove_illumina_truseq_stranded_mrna_set_b),
    ]
