# -*- coding: utf-8 -*-
# Generated by Django 1.9.8.dev20160628165209 on 2016-08-03 21:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0040_auto_20160717_1835'),
    ]

    operations = [
        migrations.CreateModel(
            name='FakRes',
            fields=[
                ('id_dok', models.IntegerField(primary_key=True, serialize=False)),
                ('k_rach', models.CharField(max_length=20)),
                ('przyczyna', models.CharField(max_length=120)),
            ],
            options={
                'db_table': 'fak_res',
                'managed': False,
            },
        ),
    ]
