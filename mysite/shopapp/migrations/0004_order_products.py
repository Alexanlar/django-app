# Generated by Django 4.2 on 2023-04-25 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0003_order_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(related_name='orders', to='shopapp.product'),
        ),
    ]