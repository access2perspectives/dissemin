# Generated by Django 2.2.17 on 2020-12-08 10:26

from django.db import migrations, models
import django_better_admin_arrayfield.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('papers', '0001_squashed_0059_remove_django_geojson'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institution',
            name='identifiers',
            field=django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(max_length=256), blank=True, null=True, size=None),
        ),
    ]