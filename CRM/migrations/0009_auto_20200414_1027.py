# Generated by Django 2.2.5 on 2020-04-14 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0008_auto_20200405_0405'),
    ]

    operations = [
        migrations.AddField(
            model_name='etisusers',
            name='api_key',
            field=models.CharField(max_length=500, null=True, verbose_name='Api key for Android'),
        ),
        migrations.AlterField(
            model_name='etisusers',
            name='password',
            field=models.CharField(max_length=500, null=True, verbose_name='Password Etis'),
        ),
    ]
