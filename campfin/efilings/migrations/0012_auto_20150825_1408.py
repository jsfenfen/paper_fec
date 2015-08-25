# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('efilings', '0011_auto_20150825_1244'),
    ]

    operations = [
        migrations.RenameField(
            model_name='filing',
            old_name='form_line_dict',
            new_name='header_data',
        ),
    ]
