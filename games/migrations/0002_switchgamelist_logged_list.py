# Generated by Django 2.1 on 2019-01-28 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='switchgamelist',
            name='logged_list',
            field=models.BooleanField(default=False),
        ),
    ]
