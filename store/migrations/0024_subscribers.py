# Generated by Django 4.0.1 on 2022-03-02 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0023_remove_guestshippingaddress_guest_customer'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscribers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, null=True)),
                ('email', models.CharField(max_length=200, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]