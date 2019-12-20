# Generated by Django 2.2.7 on 2019-11-28 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aids', '0091_auto_20191126_0949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aid',
            name='financers',
            field=models.ManyToManyField(related_name='financed_aids', to='backers.Backer', verbose_name='Financers'),
        ),
        migrations.AlterField(
            model_name='aid',
            name='instructors',
            field=models.ManyToManyField(blank=True, related_name='instructed_aids', to='backers.Backer', verbose_name='Instructors'),
        ),
    ]
