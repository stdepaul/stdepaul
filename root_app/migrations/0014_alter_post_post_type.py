# Generated by Django 3.2 on 2022-12-12 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('root_app', '0013_auto_20221212_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='post_type',
            field=models.CharField(blank=True, choices=[('HLPR', 'helpers'), ('HLPE', 'helpees')], max_length=255, null=True),
        ),
    ]