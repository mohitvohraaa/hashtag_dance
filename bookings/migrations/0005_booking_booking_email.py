# Generated by Django 5.2.1 on 2025-05-31 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0004_remove_booking_unique_completed_booking'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='booking_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
