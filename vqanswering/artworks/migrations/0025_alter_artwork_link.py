# Generated by Django 4.1.7 on 2024-01-12 11:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("artworks", "0024_alter_artwork_web_link"),
    ]

    operations = [
        migrations.AlterField(
            model_name="artwork",
            name="link",
            field=models.CharField(blank=True, default="-", max_length=200),
        ),
    ]
