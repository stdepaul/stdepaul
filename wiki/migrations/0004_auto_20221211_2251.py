# Generated by Django 3.2 on 2022-12-11 22:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0003_auto_20221211_2204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wikientry',
            name='cover_photo',
            field=models.ImageField(blank=True, null=True, upload_to='helper_cover_photos'),
        ),
        migrations.AlterField(
            model_name='wikientry',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='helper_thumbnails'),
        ),
    ]
