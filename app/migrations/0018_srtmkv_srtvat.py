# -*- coding: utf-8 -*-
# Generated by Django 1.9.6.dev20160421010813 on 2016-05-17 18:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_auto_20160516_1717'),
    ]

    operations = [
        migrations.CreateModel(
            name='SrtMkv',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nr_inw', models.CharField(max_length=20)),
                ('nazwa', models.CharField(max_length=160)),
                ('nr_faktury', models.CharField(max_length=40)),
                ('data_ot', models.DateField()),
            ],
            options={
                'db_table': 'srt_mkv',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SrtVat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rok', models.SmallIntegerField()),
                ('proporcja', models.DecimalField(decimal_places=2, max_digits=5)),
                ('zmiana_p', models.DecimalField(decimal_places=2, max_digits=5)),
                ('vat_do_odlicz', models.DecimalField(decimal_places=2, max_digits=16)),
                ('roznica_vat', models.DecimalField(decimal_places=2, max_digits=16)),
                ('korekta_vat', models.DecimalField(decimal_places=2, max_digits=16)),
            ],
            options={
                'db_table': 'srt_vat',
                'managed': False,
            },
        ),
    ]