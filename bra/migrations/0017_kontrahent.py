# -*- coding: utf-8 -*-
# Generated by Django 1.9.14.dev20170906233242 on 2019-12-29 15:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bra', '0016_auto_20170315_2247'),
    ]

    operations = [
        migrations.CreateModel(
            name='Kontrahent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nip', models.CharField(max_length=30)),
                ('nazwa1', models.CharField(max_length=255)),
            ],
        ),
    ]
