import datetime

from django.db import models


class Admin(models.Model):
    """ 管理员/用户 """
    avatar = models.FileField(verbose_name='头像', max_length=128, upload_to='avatar/',
                              null=True, blank=True)
    name = models.CharField(verbose_name='姓名', max_length=32)
    username = models.CharField(verbose_name='用户名', max_length=32)
    password = models.CharField(verbose_name='密码', max_length=64)
    mobile = models.CharField(verbose_name='手机号', max_length=11, null=True, blank=True)
    creat_time = models.DateTimeField(verbose_name='创建时间',
                                      auto_now_add=True,
                                      null=True)
    update_time = models.DateTimeField(verbose_name='更新时间',
                                       auto_now=True,
                                       null=True)

    type_choices = (
        (1, '管理员'),
        (2, '用户'),
    )
    type = models.SmallIntegerField(verbose_name='账户类型', choices=type_choices, default=2)

    card = models.CharField(verbose_name='车牌号', max_length=12, null=True, blank=True)

    def __str__(self):
        return self.username


class Park(models.Model):
    """ 车位 """
    park_id = models.CharField(verbose_name='车位编号', max_length=8)

    status_choices = (
        (1, '已占用'),
        (2, '未占用'),
    )
    park_status = models.SmallIntegerField(verbose_name='车位状态', choices=status_choices, default=2)

    def __str__(self):
        return self.park_id


class Price(models.Model):
    """ 停车区价格 """
    area = models.CharField(verbose_name='停车区', max_length=16)
    price = models.IntegerField(verbose_name='价格')


class Order(models.Model):
    """ 订单 """
    car_image = models.FileField(verbose_name='车辆照片', max_length=128, upload_to='card/',
                                 null=True, blank=True)
    order_id = models.CharField(verbose_name='订单编号', max_length=64)
    park_id = models.ForeignKey(verbose_name='车位编号', to='Park', to_field='id',
                                null=True, blank=True, on_delete=models.SET_NULL)
    card = models.CharField(verbose_name='车牌号', max_length=12)
    start_time = models.DateTimeField(verbose_name='驶入时间', auto_now_add=True)
    end_time = models.DateTimeField(verbose_name='驶出时间', null=True, blank=True)

    status_choices = (
        (1, '已完成'),
        (2, '未完成'),
    )
    status = models.SmallIntegerField(verbose_name='订单状态', choices=status_choices, default=2)
    price = models.FloatField(verbose_name='累计金额')

    def __str__(self):
        return self.park_id


class Message(models.Model):
    """ 系统消息 """
    card = models.CharField(verbose_name='车牌号', max_length=12, null=True, blank=True)
    order_id = models.CharField(verbose_name='订单编号', max_length=64, null=True, blank=True)
    start_time = models.DateTimeField(verbose_name='驶入时间', null=True, blank=True)
    end_time = models.DateTimeField(verbose_name='驶出时间', null=True, blank=True)
    park_id = models.ForeignKey(verbose_name='车位编号', to='Park', to_field='id',
                                null=True, blank=True, on_delete=models.SET_NULL)

    is_read_choices = (
        (1, '已读'),
        (2, '未读'),
    )
    is_read = models.SmallIntegerField(verbose_name='管理员消息状态', choices=is_read_choices, default=2)
    user_is_read = models.SmallIntegerField(verbose_name='用户消息状态', choices=is_read_choices, default=2)
    price = models.FloatField(verbose_name='累计金额', null=True, blank=True)

    status_choices = (
        (1, '已完成'),
        (2, '未完成'),
    )
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choices, default=2)
