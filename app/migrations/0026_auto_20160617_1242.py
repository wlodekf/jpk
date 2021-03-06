# -*- coding: utf-8 -*-
# Generated by Django 1.9.6.dev20160421010813 on 2016-06-17 12:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0025_plik_rachunek'),
    ]

    operations = [
        migrations.CreateModel(
            name='DefZrv',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('kod', models.CharField(max_length=10)),
                ('zrv', models.CharField(max_length=3)),
                ('odlicz', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('uwagi', models.CharField(max_length=100)),
                ('rok', models.SmallIntegerField()),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'def_zrv',
                'managed': False,
            },
        ),
        migrations.AlterField(
            model_name='plik',
            name='rachunek',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
