# Generated by Django 5.2.1 on 2025-05-29 03:12

import mdeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='objects',
            name='md',
            field=mdeditor.fields.MDTextField(blank=True, null=True),
        ),
    ]
