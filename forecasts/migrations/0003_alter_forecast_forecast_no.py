# Generated by Django 4.2.6 on 2023-10-24 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecasts', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forecast',
            name='forecast_no',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Request No.'),
        ),
    ]
