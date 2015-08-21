# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('efilings', '0003_auto_20150821_0532'),
    ]

    operations = [
        migrations.AddField(
            model_name='filing',
            name='form_line_data',
            field=models.TextField(null=True),
        ),
    ]
