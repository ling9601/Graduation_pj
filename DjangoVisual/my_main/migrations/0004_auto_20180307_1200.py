# Generated by Django 2.0.2 on 2018-03-07 04:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_main', '0003_scrapyitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scrapyitem',
            name='task_id',
            field=models.CharField(max_length=50),
        ),
    ]
