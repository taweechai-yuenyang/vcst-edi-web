# Generated by Django 4.2.6 on 2023-10-21 10:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('books', '0001_initial'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookdetail',
            name='factory_id',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.factory', verbose_name='From Whs'),
        ),
        migrations.AddField(
            model_name='book',
            name='corporation_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.corporation'),
        ),
        migrations.AddField(
            model_name='book',
            name='filter_product_type',
            field=models.ManyToManyField(blank=True, null=True, to='products.producttype', verbose_name='Filter Product Type ID'),
        ),
        migrations.AddField(
            model_name='book',
            name='order_type_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='books.reftype', verbose_name='Type ID'),
        ),
    ]
