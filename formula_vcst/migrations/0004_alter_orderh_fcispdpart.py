# Generated by Django 4.2.6 on 2023-10-30 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formula_vcst', '0003_alter_orderh_fcispdpart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderh',
            name='FCISPDPART',
            field=models.CharField(blank=True, db_column='FCISPDPART', default='', max_length=1, null=True),
        ),
    ]