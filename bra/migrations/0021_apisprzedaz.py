# -*- coding: utf-8 -*-
# Generated by Django 1.9.14.dev20170906233242 on 2020-02-21 18:00
from __future__ import unicode_literals

import app.model_fields
import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0073_auto_20200221_1800'),
        ('bra', '0020_importzakupow_xls'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiSprzedaz',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('od_daty', models.DateField(verbose_name='Od daty')),
                ('do_daty', models.DateField(verbose_name='Do daty')),
                ('ile_faktur', models.SmallIntegerField(default=0)),
                ('ile_wierszy', models.SmallIntegerField(default=0)),
                ('ile_kon', models.SmallIntegerField(default=0)),
                ('ile_nie_fa', models.SmallIntegerField(default=0)),
                ('ile_lp_roz', models.SmallIntegerField(default=0)),
                ('ile_podobne', models.SmallIntegerField(default=0)),
                ('od_fak_id', models.IntegerField(default=0, null=True)),
                ('do_fak_id', models.IntegerField(default=0, null=True)),
                ('kiedy', models.DateTimeField(default=datetime.datetime.now)),
                ('kto', models.CharField(max_length=10)),
                ('xls', app.model_fields.CompressedTextField(null=True, verbose_name='Plik kontrolny')),
                ('firma', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Firma')),
            ],
        ),
    ]
