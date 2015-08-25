# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('efilings', '0009_filing_filing_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='filing',
            name='form_line_data',
        ),
        migrations.AddField(
            model_name='filing',
            name='form_line_dict',
            field=django_hstore.fields.SerializedDictionaryField(help_text=b'Dictionary field of the raw form line.', null=True),
        ),
    ]
