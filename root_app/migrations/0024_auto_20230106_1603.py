# Generated by Django 3.2 on 2023-01-06 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('root_app', '0023_auto_20221214_2349'),
    ]

    operations = [
        migrations.AddField(
            model_name='helper',
            name='latitude',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='helper',
            name='longitude',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
