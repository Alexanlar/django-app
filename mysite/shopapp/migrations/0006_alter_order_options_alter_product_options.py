# Generated by Django 4.2 on 2023-07-25 11:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0005_product_created_by'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'verbose_name': 'Order', 'verbose_name_plural': 'Orders'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': 'Product', 'verbose_name_plural': 'Products'},
        ),
    ]