# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('efilings', '0004_filing_form_line_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='Update_Time',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.SlugField()),
                ('update_time', models.DateTimeField()),
            ],
        ),
        migrations.AddField(
            model_name='filing',
            name='discovery_method',
            field=models.CharField(help_text=b'How did we detect the filing? ', max_length=1, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='filing',
            name='process_time',
            field=models.DateTimeField(help_text=b'This is the time that we first located the filing', null=True, blank=True),
        ),
    ]
