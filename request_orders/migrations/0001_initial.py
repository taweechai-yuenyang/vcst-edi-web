# Generated by Django 4.2.6 on 2023-10-10 12:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('books', '0002_initial'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestOrder',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='PRIMARY KEY')),
                ('ro_no', models.CharField(blank=True, max_length=50, null=True, verbose_name='Request No.')),
                ('ro_date', models.DateField(blank=True, null=True, verbose_name='Request Date')),
                ('ro_item', models.IntegerField(blank=True, default='0', null=True, verbose_name='Item')),
                ('ro_qty', models.FloatField(blank=True, default='0', null=True, verbose_name='Qty.')),
                ('ro_price', models.FloatField(blank=True, default='0', null=True, verbose_name='Price.')),
                ('ro_status', models.CharField(choices=[('0', 'Wait Approve'), ('1', 'Approve'), ('2', 'Reject')], default='0', max_length=1, verbose_name='Request Status')),
                ('supplier_download_count', models.IntegerField(blank=True, default='0', null=True, verbose_name='Supplier Download Count')),
                ('ref_formula_id', models.CharField(blank=True, max_length=8, null=True, verbose_name='Ref. Formula ID')),
                ('is_sync', models.BooleanField(default=True, verbose_name='Is Sync')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('book_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='books.book', verbose_name='Book ID')),
            ],
            options={
                'verbose_name': 'RO',
                'verbose_name_plural': '2.Request Order',
                'db_table': 'ediRO',
                'ordering': ('ro_status', 'ro_date', 'ro_no'),
            },
        ),
        migrations.CreateModel(
            name='UploadEDI',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='PRIMARY KEY')),
                ('edi_file', models.FileField(upload_to='static/edi/%Y-%m-%d/', verbose_name='FILE EDI')),
                ('edi_filename', models.CharField(blank=True, max_length=150, null=True, verbose_name='FILE EDI')),
                ('document_no', models.CharField(blank=True, editable=False, max_length=150, null=True, verbose_name='Document No.')),
                ('upload_date', models.DateField(default=django.utils.timezone.now, verbose_name='Upload On')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('is_generated', models.BooleanField(default=False, verbose_name='Is Generated')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('book_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='books.book', verbose_name='Book ID')),
                ('revise_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='books.edirevisetype', verbose_name='Revise Type ID')),
                ('section_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.section', verbose_name='Section ID')),
                ('supplier_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.supplier', verbose_name='Supplier ID')),
                ('upload_by_id', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Upload By ID')),
            ],
            options={
                'verbose_name': 'FileEDI',
                'verbose_name_plural': '1.Upload File EDI',
                'db_table': 'ediFileUpload',
            },
        ),
        migrations.CreateModel(
            name='RequestOrderDetail',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='PRIMARY KEY')),
                ('seq', models.IntegerField(blank=True, default='0', null=True, verbose_name='Sequence')),
                ('request_qty', models.FloatField(default='0.0', verbose_name='Request Qty.')),
                ('balance_qty', models.FloatField(default='0.0', verbose_name='Balance Qty.')),
                ('price', models.FloatField(blank=True, default='0', null=True, verbose_name='Price.')),
                ('request_status', models.CharField(choices=[('0', 'Wait Approve'), ('1', 'Approve'), ('2', 'Reject')], default='0', max_length=1, verbose_name='Request Status')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='Remark')),
                ('is_selected', models.BooleanField(default=False, verbose_name='Is Selected')),
                ('is_sync', models.BooleanField(default=True, verbose_name='Is Sync')),
                ('ref_formula_id', models.CharField(blank=True, max_length=8, null=True, verbose_name='Ref. Formula ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product', verbose_name='Product ID')),
                ('request_by_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Request By ID')),
                ('request_order_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='request_orders.requestorder', verbose_name='Request ID')),
            ],
            options={
                'verbose_name': 'RO Detail',
                'verbose_name_plural': 'Request Order Detail',
                'db_table': 'ediRODetail',
                'ordering': ('seq', 'product_id', 'created_at', 'updated_at'),
            },
        ),
        migrations.AddField(
            model_name='requestorder',
            name='edi_file_id',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='request_orders.uploadedi', verbose_name='EDI File ID'),
        ),
        migrations.AddField(
            model_name='requestorder',
            name='product_group_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.productgroup', verbose_name='Model ID'),
        ),
        migrations.AddField(
            model_name='requestorder',
            name='ro_by_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Request By ID'),
        ),
        migrations.AddField(
            model_name='requestorder',
            name='section_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.section', verbose_name='Section ID'),
        ),
        migrations.AddField(
            model_name='requestorder',
            name='supplier_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.supplier', verbose_name='Supplier ID'),
        ),
        migrations.CreateModel(
            name='ApproveRequestOrder',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='PRIMARY KEY')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('request_status', models.CharField(choices=[('0', 'Wait Approve'), ('1', 'Approve'), ('2', 'Reject')], default='0', max_length=1, verbose_name='Request Status')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('request_by_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Request By ID')),
                ('request_order_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='request_orders.requestorder', verbose_name='Request ID')),
            ],
            options={
                'verbose_name': 'Approve RO',
                'verbose_name_plural': 'Approve Request Order',
                'db_table': 'ediROApprove',
            },
        ),
    ]
