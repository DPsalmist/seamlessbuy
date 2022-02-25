# Generated by Django 4.0.1 on 2022-02-25 21:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default='default_profile_pic.jpeg', upload_to='profile_pics')),
                ('gender', models.CharField(choices=[('Select Gender', 'Select Gender'), ('Male', 'Male'), ('Female', 'Female')], default='Select Gender', max_length=30)),
                ('bvn', models.CharField(default=0, max_length=30)),
                ('bank', models.CharField(default='State Your Bank', max_length=30)),
                ('phone_no', models.CharField(default=0, max_length=30)),
                ('address', models.TextField(default='my address', max_length=150)),
                ('account_no', models.CharField(default=0, max_length=30)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
