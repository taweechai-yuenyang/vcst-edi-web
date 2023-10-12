# Generated by Django 4.2.6 on 2023-10-12 14:33

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='PRIMARY KEY')),
                ('skid', models.CharField(max_length=50, unique=True, verbose_name='Key')),
                ('code', models.CharField(max_length=50, verbose_name='Code')),
                ('name', models.CharField(max_length=250, verbose_name='Name')),
                ('prefix', models.CharField(blank=True, max_length=250, null=True, verbose_name='Prefix')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Book',
                'verbose_name_plural': 'Book',
                'db_table': 'tbmBook',
            },
        ),
        migrations.CreateModel(
            name='EDIReviseType',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='PRIMARY KEY')),
                ('code', models.IntegerField(unique=True, verbose_name='Code')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Revise Type',
                'verbose_name_plural': 'Revise Type',
                'db_table': 'tbmReviseType',
            },
        ),
        migrations.CreateModel(
            name='RefType',
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
                'verbose_name': 'Ref Type',
                'verbose_name_plural': 'Ref Type',
                'db_table': 'tbmRefType',
            },
        ),
        migrations.CreateModel(
            name='ReviseBook',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='PRIMARY KEY')),
                ('name', models.CharField(max_length=250, unique=True, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('is_active', models.BooleanField(blank=True, default=True, null=True, verbose_name='Is Active')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('book_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='books.book', verbose_name='Book ID')),
                ('ref_type_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='books.reftype', verbose_name='Ref. Type ID')),
            ],
            options={
                'verbose_name': 'Revise Book',
                'verbose_name_plural': 'Revise Book',
                'db_table': 'tbmReviseBook',
            },
        ),
        migrations.CreateModel(
            name='BookDetail',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='PRIMARY KEY')),
                ('factory_type', models.CharField(choices=[('F', 'Form Whs'), ('T', 'To Whs')], max_length=1, verbose_name='Book Ref')),
                ('is_active', models.BooleanField(blank=True, default=True, null=True, verbose_name='Is Active')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('book_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='books.book', verbose_name='Book ID')),
            ],
            options={
                'verbose_name': 'Book Detail',
                'verbose_name_plural': 'Book Detail',
                'db_table': 'tbmBookDetail',
            },
        ),
    ]
