# Generated by Django 3.1 on 2020-09-05 17:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('artworks', '0008_question_answer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question_answer',
            name='title',
            field=models.CharField(max_length=300),
        ),
    ]
