# Generated by Django 3.1 on 2020-08-25 14:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('artworks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artwork',
            name='year',
            field=models.DecimalField(decimal_places=0, max_digits=4),
        ),
    ]
