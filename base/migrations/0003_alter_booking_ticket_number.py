# Generated by Django 4.2.3 on 2023-07-24 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_alter_booking_ticket_number_alter_booking_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='ticket_number',
            field=models.CharField(default='e8ca4aef66', max_length=10, unique=True),
        ),
    ]
