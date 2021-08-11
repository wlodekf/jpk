# -*- coding: utf-8 -*-
# Generated by Django 1.9.14.dev20170906233242 on 2020-02-28 13:12
from __future__ import unicode_literals

import app.model_fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0075_auto_20200227_1502'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deklaracja',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grupa', models.CharField(max_length=1, verbose_name='Grupa')),
                ('lp1', models.SmallIntegerField()),
                ('nazwa', models.CharField(max_length=255, verbose_name='Nazwa')),
                ('rodzaj', models.CharField(max_length=2, verbose_name='Rodzaj')),
                ('kwota1', models.DecimalField(decimal_places=2, default=0.0, max_digits=16, verbose_name='Kwota1')),
                ('kwota2', models.DecimalField(decimal_places=2, default=0.0, max_digits=16, verbose_name='Kwota2')),
                ('wybor', models.BooleanField(default=False, verbose_name='Wybor')),
                ('tekst', app.model_fields.CompressedTextField(null=True, verbose_name='Opis zasad')),
            ],
        ),
        migrations.RemoveField(
            model_name='plik',
            name='kod_systemowy',
        ),
        migrations.RemoveField(
            model_name='plik',
            name='wariant_formularza',
        ),
        migrations.RemoveField(
            model_name='plik',
            name='wersja_schemy',
        ),
        migrations.AddField(
            model_name='plik',
            name='wariant_dek',
            field=models.SmallIntegerField(default=21),
        ),
        migrations.AddField(
            model_name='deklaracja',
            name='jpk',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Plik'),
        ),
    ]