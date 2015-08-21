# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('efilings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='filing',
            name='skeda_linecount',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='filing',
            name='skedb_linecount',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='filing',
            name='skedc_linecount',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='filing',
            name='skedd_linecount',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='filing',
            name='skede_linecount',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='filing',
            name='skedo_linecount',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
