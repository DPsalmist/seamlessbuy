# Generated by Django 4.0.1 on 2022-02-25 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_order_paid_alter_order_complete_loan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='complete',
            field=models.CharField(choices=[('Unapproved', 'Unapproved'), ('Pending', 'Pending'), ('Delivered', 'Delivered')], default='Pending', max_length=30),
        ),
    ]
