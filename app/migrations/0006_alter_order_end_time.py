# Generated by Django 4.0.3 on 2022-04-23 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='end_time',
            field=models.DateTimeField(verbose_name='驶出时间'),
        ),
    ]
