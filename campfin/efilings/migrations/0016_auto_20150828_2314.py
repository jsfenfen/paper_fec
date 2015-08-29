# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('efilings', '0015_auto_20150828_1843'),
    ]

    operations = [
        migrations.RenameField(
            model_name='committee',
            old_name='total_unitemized',
            new_name='total_unitemized_indiv',
        ),
        migrations.AddField(
            model_name='committee',
            name='total_itemized_indiv',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2),
        ),
    ]
