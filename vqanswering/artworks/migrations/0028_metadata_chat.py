# Generated by Django 4.1.7 on 2024-09-03 13:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('artworks', '0027_artwork_description_validated_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='Metadata',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=100)),
                ('link', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('weblink', models.CharField(blank=True, default='-', max_length=255)),
                ('museumgroup', models.CharField(default='Is not shared', max_length=200)),
                ('artwork', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='artworks.artwork')),
            ],
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('answer', models.TextField()),
                ('question_language', models.CharField(default='English', max_length=50)),
                ('resolved', models.BooleanField(default=False)),
                ('artwork', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='artworks.artwork')),
            ],
        ),
    ]
