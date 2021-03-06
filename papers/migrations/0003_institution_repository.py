# Generated by Django 2.2.17 on 2020-12-08 13:26

import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('deposit', '0026_letter_declaration_url'),
        ('papers', '0002_better_arrayfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='repository',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='deposit.Repository'),
        ),
        migrations.AddIndex(
            model_name='institution',
            index=django.contrib.postgres.indexes.GinIndex(fields=['identifiers'], name='papers_inst_identif_e468e7_gin'),
        ),
    ]
