# Generated by Django 4.0.1 on 2022-03-02 05:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0020_guestshippingaddress_email_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guestshippingaddress',
            name='email',
            field=models.EmailField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='guestshippingaddress',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.guestorder'),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='email',
            field=models.EmailField(max_length=200, null=True),
        ),
    ]