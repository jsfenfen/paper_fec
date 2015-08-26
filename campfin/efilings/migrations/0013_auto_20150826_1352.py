# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('efilings', '0012_auto_20150825_1408'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='filing',
            name='skeda_linecount',
        ),
        migrations.RemoveField(
            model_name='filing',
            name='skedb_linecount',
        ),
        migrations.RemoveField(
            model_name='filing',
            name='skedc_linecount',
        ),
        migrations.RemoveField(
            model_name='filing',
            name='skedd_linecount',
        ),
        migrations.RemoveField(
            model_name='filing',
            name='skede_linecount',
        ),
        migrations.RemoveField(
            model_name='filing',
            name='skedo_linecount',
        ),
        migrations.AddField(
            model_name='filing',
            name='lines_present',
            field=django_hstore.fields.SerializedDictionaryField(help_text=b'How many itemization lines are present of which type', null=True),
        ),
    ]
