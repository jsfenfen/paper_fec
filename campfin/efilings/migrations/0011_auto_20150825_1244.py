# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('efilings', '0010_auto_20150825_1242'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='otherline',
            name='line_data',
        ),
        migrations.AddField(
            model_name='otherline',
            name='line_dict',
            field=django_hstore.fields.SerializedDictionaryField(help_text=b'Dictionary field of the raw form line.', null=True),
        ),
    ]
