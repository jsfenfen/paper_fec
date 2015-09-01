# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('efilings', '0018_auto_20150831_1742'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='total_itemized_indiv',
            field=models.DecimalField(default=0, help_text=b'itemized contributions from individuals', null=True, max_digits=19, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='total_unitemized_indiv',
            field=models.DecimalField(default=0, help_text=b'Unitemized contributions from individuals', null=True, max_digits=19, decimal_places=2),
        ),
    ]
