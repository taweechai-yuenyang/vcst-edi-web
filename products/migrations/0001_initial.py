# Generated by Django 4.2.6 on 2023-10-10 10:41

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProductGroup',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='PRIMARY KEY')),
                ('code', models.CharField(max_length=50, unique=True, verbose_name='Code')),
                ('name', models.CharField(max_length=250, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Product Group',
                'verbose_name_plural': 'Product Group',
                'db_table': 'tbmProductGroup',
            },
        ),
        migrations.CreateModel(
            name='ProductType',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='PRIMARY KEY')),
                ('code', models.CharField(max_length=50, unique=True, verbose_name='Code')),
                ('name', models.CharField(max_length=250, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Product Type',
                'verbose_name_plural': 'Product Type',
                'db_table': 'tbmProductType',
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='PRIMARY KEY')),
                ('code', models.CharField(max_length=50, unique=True, verbose_name='Code')),
                ('name', models.CharField(max_length=250, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Unit',
                'verbose_name_plural': 'Unit',
                'db_table': 'tbmUnit',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='PRIMARY KEY')),
                ('code', models.CharField(max_length=150, unique=True, verbose_name='Code')),
                ('name', models.CharField(max_length=250, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('img', models.ImageField(upload_to='', verbose_name='Image')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('prod_group_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.productgroup', verbose_name='Product Group ID')),
                ('prod_type_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.producttype', verbose_name='Product Type ID')),
                ('unit_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.unit', verbose_name='Unit ID')),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Product',
                'db_table': 'tbmProduct',
            },
        ),
    ]
