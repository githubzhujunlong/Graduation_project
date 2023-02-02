# Generated by Django 4.0.3 on 2022-04-22 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_park'),
    ]

    operations = [
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area', models.CharField(max_length=16, verbose_name='停车区')),
                ('price', models.IntegerField(verbose_name='价格')),
            ],
        ),
    ]
