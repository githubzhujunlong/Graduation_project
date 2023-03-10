# Generated by Django 4.0.3 on 2022-04-23 10:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('car_image', models.FileField(blank=True, max_length=128, null=True, upload_to='card/', verbose_name='车辆照片')),
                ('order_id', models.CharField(max_length=64, verbose_name='订单编号')),
                ('card', models.CharField(max_length=12, verbose_name='车牌号')),
                ('start_time', models.DateTimeField(auto_now_add=True, verbose_name='驶入时间')),
                ('end_time', models.DateTimeField(auto_now=True, verbose_name='驶出时间')),
                ('status', models.SmallIntegerField(choices=[(1, '已完成'), (2, '未完成')], default=2, verbose_name='订单状态')),
                ('price', models.IntegerField(verbose_name='累计金额')),
                ('park_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.park', verbose_name='车位编号')),
            ],
        ),
    ]
