# Generated by Django 5.1.1 on 2025-06-23 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_order_pincode'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('CARD', 'Card'), ('PHONEPE', 'PhonePe'), ('GPAY', 'Google Pay'), ('COD', 'Cash on Delivery')], default='COD', max_length=10),
        ),
        migrations.AlterField(
            model_name='order',
            name='pincode',
            field=models.CharField(default='', max_length=10),
        ),
        migrations.AlterField(
            model_name='order',
            name='total',
            field=models.FloatField(),
        ),
    ]
