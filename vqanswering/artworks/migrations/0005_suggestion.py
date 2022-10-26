# Generated by Django 3.1 on 2020-08-28 10:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('artworks', '0004_artwork_century'),
    ]

    operations = [
        migrations.CreateModel(
            name='Suggestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=200)),
                ('message', models.TextField()),
            ],
        ),
    ]
