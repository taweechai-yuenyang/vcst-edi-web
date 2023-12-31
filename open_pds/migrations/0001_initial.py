# Generated by Django 4.2.6 on 2023-10-30 10:11

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('forecasts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PDSDetail',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='PRIMARY KEY')),
                ('seq', models.IntegerField(verbose_name='Seq.')),
                ('qty', models.FloatField(verbose_name='Qty')),
                ('price', models.FloatField(blank=True, default='0', null=True, verbose_name='Price')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='Remark')),
                ('ref_formula_id', models.CharField(blank=True, max_length=8, null=True, verbose_name='Formula ID')),
                ('is_active', models.BooleanField(blank=True, default=False, null=True, verbose_name='Is Active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'PDSDetail',
                'verbose_name_plural': 'PDS Detail',
                'db_table': 'ediPDSDetail',
                'permissions': [('create_purchase_order', 'เปิด PO'), ('edit_purchase_qty_price', 'แก้ไขจำนวน/ราคา')],
            },
        ),
        migrations.CreateModel(
            name='PDSHeader',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='PRIMARY KEY')),
                ('pds_date', models.DateField(blank=True, null=True, verbose_name='PDS Date')),
                ('pds_no', models.CharField(blank=True, max_length=15, null=True, verbose_name='PDS No.')),
                ('item', models.IntegerField(verbose_name='Item')),
                ('qty', models.FloatField(verbose_name='Qty')),
                ('summary_price', models.FloatField(blank=True, default='0', null=True, verbose_name='Summary Price')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='Remark')),
                ('pds_status', models.CharField(blank=True, choices=[('0', 'In Progress'), ('1', 'Approve'), ('2', 'Success'), ('3', 'Reject')], default='0', max_length=1, null=True, verbose_name='PDS Status')),
                ('ref_formula_id', models.CharField(blank=True, max_length=8, null=True, verbose_name='Formula ID')),
                ('is_active', models.BooleanField(blank=True, default=False, null=True, verbose_name='Is Active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('forecast_id', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='forecasts.forecast', verbose_name='Forecast ID')),
            ],
            options={
                'verbose_name': 'PDS',
                'verbose_name_plural': 'EDI PDS',
                'db_table': 'ediPDS',
                'ordering': ('pds_status', 'pds_no', 'created_at', 'updated_at'),
                'permissions': [('create_purchase_order', 'เปิด PO'), ('is_download_report', 'ดูรายงาน')],
            },
        ),
    ]
