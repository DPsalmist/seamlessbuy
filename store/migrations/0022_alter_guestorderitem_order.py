# Generated by Django 4.0.1 on 2022-03-02 05:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0021_alter_guestshippingaddress_email_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guestorderitem',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.guestorder'),
        ),
    ]