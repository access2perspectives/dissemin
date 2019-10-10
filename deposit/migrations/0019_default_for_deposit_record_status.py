# Generated by Django 2.2.4 on 2019-10-07 07:12

from django.db import migrations, models


def empty_to_failed(apps, schema_editor):
    """
    Changes status of each DepositRecord with empty value to 'failed'.
    """
    DepositRecord = apps.get_model('deposit', 'DepositRecord')

    DepositRecord.objects.filter(status='').update(status='failed')


def failed_to_empty(apps, schema_editor):
    """
    Changes status of each DepositRecord with value 'failed' to empty value.
    """
    DepositRecord = apps.get_model('deposit', 'DepositRecord')

    DepositRecord.objects.filter(status='failed').update(status='')


class Migration(migrations.Migration):

    dependencies = [
        ('deposit', '0018_letter_of_declaration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='depositrecord',
            name='status',
            field=models.CharField(choices=[('failed', 'Failed'), ('faked', 'Faked'), ('pending', 'Pending publication'), ('published', 'Published'), ('refused', 'Refused by the repository'), ('deleted', 'Deleted')], default='failed', max_length=64),
        ),
        migrations.RunPython(empty_to_failed, failed_to_empty),
    ]
