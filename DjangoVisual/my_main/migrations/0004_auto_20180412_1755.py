# Generated by Django 2.0.2 on 2018-04-12 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_main', '0003_auto_20180412_1104'),
    ]

    operations = [
        migrations.CreateModel(
            name='comments_Item_dj',
            fields=[
                ('created_at', models.CharField(max_length=20)),
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('like_counts', models.IntegerField()),
                ('source', models.CharField(max_length=50, null=True)),
                ('text', models.TextField()),
                ('user_id', models.CharField(max_length=100)),
                ('screen_name', models.CharField(max_length=30)),
                ('post_id', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='new_post_Item_dj',
            fields=[
                ('attitudes_count', models.IntegerField()),
                ('comments_count', models.IntegerField()),
                ('created_at', models.CharField(max_length=20)),
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('reposts_count', models.IntegerField()),
                ('text', models.TextField()),
                ('retweeted_status', models.BooleanField()),
                ('retweeted_text', models.TextField(null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='post_item_dj',
            name='is_crawl',
        ),
    ]