# Generated by Django 4.2.6 on 2023-10-21 16:24

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileForecast',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='PRIMARY KEY')),
                ('edi_file', models.FileField(upload_to='static/edi/%Y-%m-%d/', verbose_name='File Forecast')),
                ('edi_filename', models.CharField(blank=True, max_length=150, null=True, verbose_name='File Forecast')),
                ('document_no', models.CharField(blank=True, editable=False, max_length=150, null=True, verbose_name='Document No.')),
                ('upload_date', models.DateField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='Upload On')),
                ('upload_on_month', models.IntegerField(blank=True, default='0', null=True, verbose_name='Upload On Month')),
                ('upload_seq', models.IntegerField(blank=True, default='0', null=True, verbose_name='Upload Seq')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('is_generated', models.BooleanField(blank=True, default=False, null=True, verbose_name='Is Generated')),
                ('is_active', models.BooleanField(blank=True, default=False, null=True, verbose_name='Is Active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Upload',
                'verbose_name_plural': 'Upload Forecast',
                'db_table': 'ediFileUpload',
                'permissions': [('add_file', 'อัพโหลดข้อมูล')],
            },
        ),
        migrations.CreateModel(
            name='Forecast',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='PRIMARY KEY')),
                ('forecast_no', models.CharField(blank=True, max_length=10, null=True, verbose_name='Request No.')),
                ('forecast_date', models.DateField(blank=True, null=True, verbose_name='Request Date')),
                ('forecast_on_month', models.IntegerField(blank=True, default='0', null=True, verbose_name='Request On Month')),
                ('forecast_item', models.IntegerField(blank=True, default='0', null=True, verbose_name='Item')),
                ('forecast_qty', models.FloatField(blank=True, default='0', null=True, verbose_name='Qty.')),
                ('forecast_price', models.FloatField(blank=True, default='0', null=True, verbose_name='Price.')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='Remark')),
                ('forecast_status', models.CharField(choices=[('0', 'In Progress'), ('1', 'Approve'), ('2', 'Success'), ('3', 'Reject')], default='0', max_length=1, verbose_name='Request Status')),
                ('supplier_download_count', models.IntegerField(blank=True, default='0', null=True, verbose_name='Supplier Download Count')),
                ('ref_formula_id', models.CharField(blank=True, max_length=8, null=True, verbose_name='Ref. Formula ID')),
                ('is_po', models.BooleanField(blank=True, default=False, null=True, verbose_name='Is PO')),
                ('is_sync', models.BooleanField(blank=True, default=True, null=True, verbose_name='Is Sync')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Forecast',
                'verbose_name_plural': 'Upload Forecast',
                'db_table': 'ediForecast',
                'ordering': ('forecast_status', 'forecast_date', 'forecast_no'),
                'permissions': [('approve_reject', 'Approve/Reject')],
            },
        ),
        migrations.CreateModel(
            name='ForecastDetail',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='PRIMARY KEY')),
                ('seq', models.IntegerField(blank=True, default='0', null=True, verbose_name='Sequence')),
                ('request_qty', models.FloatField(default='0.0', verbose_name='Request Qty.')),
                ('balance_qty', models.FloatField(default='0.0', verbose_name='Balance Qty.')),
                ('price', models.FloatField(blank=True, default='0', null=True, verbose_name='Price.')),
                ('request_status', models.CharField(choices=[('0', 'In Progress'), ('1', 'Approve'), ('2', 'Success'), ('3', 'Reject')], default='0', max_length=1, verbose_name='Request Status')),
                ('import_model_by_user', models.CharField(blank=True, max_length=255, null=True)),
                ('remark', models.TextField(blank=True, null=True, verbose_name='Remark')),
                ('is_selected', models.BooleanField(default=False, verbose_name='Is Selected')),
                ('is_sync', models.BooleanField(default=True, verbose_name='Is Sync')),
                ('ref_formula_id', models.CharField(blank=True, max_length=8, null=True, verbose_name='Ref. Formula ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('forecast_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forecasts.forecast', verbose_name='Open PDS ID')),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product', verbose_name='Product ID')),
            ],
            options={
                'verbose_name': 'ForecastDetail',
                'verbose_name_plural': 'Forecast Detail',
                'db_table': 'ediForecastDetail',
                'ordering': ('seq', 'product_id', 'created_at', 'updated_at'),
                'permissions': [('edit_qty_price', 'แก้ไขจำนวนและราคา'), ('select_item', 'เลือกรายการสินค้า')],
            },
        ),
        migrations.CreateModel(
            name='ForecastErrorLogs',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='PRIMARY KEY')),
                ('file_name', models.UUIDField(verbose_name='File Forecast')),
                ('row_num', models.IntegerField(verbose_name='Row')),
                ('item', models.IntegerField(verbose_name='Item')),
                ('part_code', models.CharField(max_length=50, verbose_name='Part Code')),
                ('part_no', models.CharField(max_length=50, verbose_name='Part No.')),
                ('part_name', models.CharField(max_length=50, verbose_name='Part Name')),
                ('supplier', models.CharField(max_length=50, verbose_name='Supplier')),
                ('model', models.CharField(max_length=50, verbose_name='Model')),
                ('rev_0', models.IntegerField(blank=True, default=0, null=True, verbose_name='Rev.0')),
                ('rev_1', models.IntegerField(blank=True, default=0, null=True, verbose_name='Rev.1')),
                ('rev_2', models.IntegerField(blank=True, default=0, null=True, verbose_name='Rev.2')),
                ('rev_3', models.IntegerField(blank=True, default=0, null=True, verbose_name='Rev.3')),
                ('rev_4', models.IntegerField(blank=True, default=0, null=True, verbose_name='Rev.4')),
                ('rev_5', models.IntegerField(blank=True, default=0, null=True, verbose_name='Rev.5')),
                ('rev_6', models.IntegerField(blank=True, default=0, null=True, verbose_name='Rev.6')),
                ('rev_7', models.IntegerField(blank=True, default=0, null=True, verbose_name='Rev.7')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='Remark')),
                ('is_error', models.BooleanField(blank=True, default=True, null=True, verbose_name='Is Error')),
                ('is_success', models.BooleanField(blank=True, default=False, null=True, verbose_name='Is Success')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'PDS Error Logging',
                'verbose_name_plural': 'PDS Error Logging',
                'db_table': 'ediForecastErrorLogs',
                'ordering': ('row_num', 'item', 'created_at', 'updated_at'),
            },
        ),
        migrations.CreateModel(
            name='PDSHeader',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='PRIMARY KEY')),
                ('pds_date', models.DateField(blank=True, null=True, verbose_name='PDS Date')),
                ('pds_no', models.CharField(blank=True, max_length=10, null=True, verbose_name='PDS No.')),
                ('item', models.IntegerField(verbose_name='Item')),
                ('qty', models.FloatField(verbose_name='Qty')),
                ('summary_price', models.FloatField(blank=True, default='0', null=True, verbose_name='Summary Price')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='Remark')),
                ('ref_formula_id', models.CharField(blank=True, max_length=8, null=True, verbose_name='Formula ID')),
                ('is_active', models.BooleanField(blank=True, default=False, null=True, verbose_name='Is Active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('forecast_id', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='forecasts.forecast', verbose_name='Forecast ID')),
            ],
            options={
                'verbose_name': 'OpenPDS',
                'verbose_name_plural': 'Open PDS',
                'db_table': 'ediPDS',
                'permissions': [('create_purchase_order', 'เปิด PO')],
            },
        ),
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
                ('forecast_detail_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forecasts.forecastdetail', verbose_name='PDS Detail')),
                ('pds_header_id', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='forecasts.pdsheader', verbose_name='PDS ID')),
            ],
            options={
                'verbose_name': 'PDSDetail',
                'verbose_name_plural': 'PDS Detail',
                'db_table': 'ediPDSDetail',
                'permissions': [('create_purchase_order', 'เปิด PO'), ('edit_purchase_qty_price', 'แก้ไขจำนวน/ราคา')],
            },
        ),
    ]
