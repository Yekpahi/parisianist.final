# Generated by Django 5.0.4 on 2024-05-10 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_on_header',
            field=models.BooleanField(default=False),
        ),
    ]