# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('efilings', '0007_auto_20150825_0120'),
    ]

    operations = [
        migrations.AddField(
            model_name='filing',
            name='filing_number',
            field=models.IntegerField(help_text=b'The integer part of the filing number assigned to this electronic filing by the FEC', null=True),
        ),
        migrations.AlterField(
            model_name='filing',
            name='filing_id',
            field=models.CharField(help_text=b'The alphanumeric filing number assigned to this electronic filing by the FEC', max_length=15, unique=True, serialize=False, primary_key=True),
        ),
    ]
