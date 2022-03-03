# Generated by Django 4.0.1 on 2022-03-02 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0019_alter_shippingaddress_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='guestshippingaddress',
            name='email',
            field=models.EmailField(max_length=200, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='guestshippingaddress',
            name='first_name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='guestshippingaddress',
            name='last_name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='shippingaddress',
            name='email',
            field=models.EmailField(max_length=200, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='address',
            field=models.CharField(max_length=200, null=True),
        ),
    ]