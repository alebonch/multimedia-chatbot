# Generated by Django 4.1.7 on 2024-01-12 11:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("artworks", "0025_alter_artwork_link"),
    ]

    operations = [
        migrations.AlterField(
            model_name="artwork",
            name="link",
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
