# Generated by Django 3.2 on 2022-12-13 02:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0010_wikientry_is_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wikientry',
            name='helper_type',
            field=models.CharField(blank=True, choices=[('food', 'Food Assistance'), ('rent_utilities', 'Housing / Rent Assistance'), ('entry_level_job', 'Entry-Level Job Employer'), ('develop_skills', 'Job Skills Educator'), ('mental_health', 'Mental Health Services Organization or Individual'), ('rehab', 'Drug / Alcohol Rehab Services Organization'), ('scholarships', 'Scholarship Offerer'), ('other', 'Other')], max_length=255, null=True),
        ),
    ]