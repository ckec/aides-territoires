# Generated by Django 2.2.1 on 2019-06-12 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookmarks', '0003_bookmark_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookmark',
            name='send_email_alert',
            field=models.BooleanField(default=False, verbose_name='Send email alert'),
        ),
    ]