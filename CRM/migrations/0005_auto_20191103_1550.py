# Generated by Django 2.2.5 on 2019-11-03 10:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0004_auto_20191024_1216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='time',
            name='worker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Работник'),
        ),
    ]