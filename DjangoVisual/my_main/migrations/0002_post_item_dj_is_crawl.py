# Generated by Django 2.0.2 on 2018-04-12 02:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post_item_dj',
            name='is_crawl',
            field=models.BooleanField(default=False),
        ),
    ]
