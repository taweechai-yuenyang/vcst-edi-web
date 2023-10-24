# Generated by Django 4.2.6 on 2023-10-24 14:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('books', '0002_initial'),
        ('forecasts', '0001_initial'),
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='forecastdetail',
            name='request_by_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Request By ID'),
        ),
        migrations.AddField(
            model_name='forecast',
            name='book_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='books.book', verbose_name='Book ID'),
        ),
        migrations.AddField(
            model_name='forecast',
            name='edi_file_id',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='forecasts.fileforecast', verbose_name='Forecast ID'),
        ),
        migrations.AddField(
            model_name='forecast',
            name='forecast_by_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Request By ID'),
        ),
        migrations.AddField(
            model_name='forecast',
            name='forecast_plan_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.planningforecast'),
        ),
        migrations.AddField(
            model_name='forecast',
            name='section_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.section', verbose_name='Section ID'),
        ),
        migrations.AddField(
            model_name='forecast',
            name='supplier_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.supplier', verbose_name='Supplier ID'),
        ),
        migrations.AddField(
            model_name='fileforecast',
            name='upload_by_id',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Upload By ID'),
        ),
    ]
