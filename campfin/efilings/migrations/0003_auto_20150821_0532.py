# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('efilings', '0002_auto_20150821_0520'),
    ]

    operations = [
        migrations.RenameField(
            model_name='otherline',
            old_name='line_number',
            new_name='line_sequence',
        ),
        migrations.RenameField(
            model_name='skeda',
            old_name='line_number',
            new_name='line_sequence',
        ),
        migrations.RenameField(
            model_name='skedb',
            old_name='line_number',
            new_name='line_sequence',
        ),
        migrations.RenameField(
            model_name='skede',
            old_name='line_number',
            new_name='line_sequence',
        ),
    ]
