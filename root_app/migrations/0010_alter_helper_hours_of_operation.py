# Generated by Django 3.2 on 2022-12-12 00:31

from django.db import migrations
import martor.models


class Migration(migrations.Migration):

    dependencies = [
        ('root_app', '0009_auto_20221211_2251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='helper',
            name='hours_of_operation',
            field=martor.models.MartorField(blank=True, null=True),
        ),
    ]