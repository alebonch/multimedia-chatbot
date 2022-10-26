# Generated by Django 3.1 on 2020-09-11 08:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('artworks', '0009_auto_20200905_1707'),
    ]

    operations = [
        migrations.AddField(
            model_name='question_answer',
            name='sentence_type',
            field=models.CharField(
                choices=[('visual sentence', 'visual sentence'), ('contextual sentence', 'contextual sentence')],
                default='contextual sentence', max_length=150),
        ),
    ]
