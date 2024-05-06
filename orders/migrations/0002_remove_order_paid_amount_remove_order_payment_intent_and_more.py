# Generated by Django 5.0.4 on 2024-05-06 00:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='paid_amount',
        ),
        migrations.RemoveField(
            model_name='order',
            name='payment_intent',
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_intent',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
