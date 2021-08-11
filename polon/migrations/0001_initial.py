# -*- coding: utf-8 -*-
# Generated by Django 1.9.13.dev20170130170755 on 2017-02-18 23:16
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Faktura',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zaklad', models.CharField(max_length=3)),
                ('temat', models.CharField(max_length=10)),
                ('fak_id', models.IntegerField()),
                ('nr_faktury', models.CharField(max_length=15)),
                ('data_wyst', models.DateField()),
                ('data_sprz', models.DateField()),
                ('zamowienie', models.CharField(max_length=20)),
                ('brutto', models.DecimalField(decimal_places=2, default=0.0, max_digits=16)),
                ('kon_id', models.IntegerField()),
                ('kon_nazwa', models.CharField(max_length=160)),
                ('kon_miejsc', models.CharField(max_length=30, null=True)),
                ('data_rozp', models.DateField()),
                ('zlc_nazwa', models.CharField(max_length=40)),
                ('zlc_tytul', models.CharField(max_length=250)),
                ('opis', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Tworzenie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zadanie', models.IntegerField()),
                ('uzytkownik', models.CharField(max_length=10)),
                ('zlecono', models.DateTimeField(default=datetime.datetime.now)),
                ('od_daty', models.DateField()),
                ('do_daty', models.DateField()),
                ('zaklady', models.CharField(max_length=50, null=True)),
                ('tematy', models.CharField(max_length=100, null=True)),
                ('pkwiu', models.CharField(max_length=100, null=True)),
                ('podpis', models.CharField(max_length=10)),
                ('ile_faktur', models.IntegerField()),
                ('tmp_dir', models.CharField(max_length=20, null=True)),
                ('zakonczono', models.DateTimeField(null=True)),
                ('ile_plikow', models.IntegerField(default=0)),
                ('rozmiar_zip', models.IntegerField(null=True)),
                ('pobrano', models.DateTimeField(null=True)),
            ],
        ),
        migrations.AddField(
            model_name='faktura',
            name='tworzenie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polon.Tworzenie'),
        ),
    ]
