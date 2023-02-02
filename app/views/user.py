import datetime
import json

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django import forms
from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from app.models import Admin, Order, Message, Price
from app.utils.bootstrap import BootStrapModelForm
from app.utils.encrypt import md5
from app.utils.pagination import Pagination
from app.views.admin import AdminModifyModelForm, AdminEditAvatarModelForm, avatar_delete
from app.views.order import OrderModelForm


class UserModelForm(BootStrapModelForm):
    # bootstrap_exclude_fields = ['avatar']
    confirm_password = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(render_value=True)
    )
    mobile = forms.CharField(
        label='手机号',
        validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误')],
    )

    class Meta:
        model = Admin
        fields = ['name', 'username', 'password', 'confirm_password', 'mobile']
        widgets = {
            'password': forms.PasswordInput(render_value=True)
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        exists = Admin.objects.filter(username=username).exists()
        if exists:
            raise ValidationError('用户名已存在')
        return username

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        return md5(pwd)

    def clean_confirm_password(self):
        # print(self.cleaned_data)
        # {'username': '111', 'password': '222', 'confirm_password': '333'}
        pwd = self.cleaned_data.get('password')
        confirm = md5(self.cleaned_data.get('confirm_password'))
        if confirm != pwd:
            raise ValidationError('密码不一致')
        # 返回的值就是要保存到数据库的值
        return confirm

    def clean_mobile(self):
        txt_mobile = self.cleaned_data['mobile']
        exists = Admin.objects.filter(mobile=txt_mobile).exists()
        if exists:
            raise ValidationError('手机号已存在')
        return txt_mobile


def user_register(request):
    """ 用户注册 """
    title = '用户注册'
    if request.method == 'GET':
        form = UserModelForm()
        return render(request, 'user_register.html', locals())
    form = UserModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('/admin/login/')
    return render(request, 'user_register.html', locals())


def user_show(request):
    """ 用户主页 """
    return render(request, 'user_show.html')


class UserEditModelForm(BootStrapModelForm):
    mobile = forms.CharField(
        label='手机号',
        validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误')],
    )

    class Meta:
        model = Admin
        fields = ['name', 'mobile', 'card']

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        exists = Admin.objects.filter(mobile=mobile).exclude(id=self.instance.pk).exists()
        if exists:
            raise ValidationError('手机号已存在')
        return mobile


def user_info(request):
    """ 个人信息 """
    id = request.session.get('info')['id']
    user_obj = Admin.objects.filter(id=id).first()
    form = UserEditModelForm()
    form2 = AdminEditAvatarModelForm()
    return render(request, 'user_info.html', locals())


def user_detail(request):
    id = request.session.get('info')['id']
    user_dict = Admin.objects.filter(id=id).values('name', 'mobile').first()
    return HttpResponse(json.dumps({'status': True, 'data': user_dict}))


@csrf_exempt
def user_edit(request):
    """ 编辑信息 """
    id = request.session.get('info')['id']
    user_obj = Admin.objects.filter(id=id).first()
    form = UserEditModelForm(data=request.POST, instance=user_obj)
    if form.is_valid():
        form.save()
        return HttpResponse(json.dumps({'status': True}))
    return HttpResponse(json.dumps({'status': False, 'error': form.errors}))


@csrf_exempt
def user_edit_avatar(request):
    id = request.session.get('info')['id']
    user_obj = Admin.objects.filter(id=id).first()
    print(request.FILES)
    form = AdminEditAvatarModelForm(files=request.FILES, instance=user_obj)
    if form.is_valid():
        form.save()
        return HttpResponse(json.dumps({'status': True}))
    return HttpResponse(json.dumps({'status': False, 'error': form.errors}))


def user_getAvatar(request):
    id = request.session.get('info')['id']
    user_obj = Admin.objects.filter(id=id).first()
    # print(admin_obj.avatar.name, type(admin_obj.avatar.name))
    return HttpResponse(json.dumps({'data': user_obj.avatar.name}))


def user_delete(request):
    """ 注销账户 """
    id = request.session.get('info')['id']
    user_obj = Admin.objects.filter(id=id)
    avatar_delete(user_obj)
    user_obj.delete()
    request.session.clear()
    return HttpResponse(json.dumps({'status': True}))


def user_order(request):
    """ 用户订单列表 """
    data_dict = {}
    user = Admin.objects.filter(id=request.session.get('info')['id']).first()
    print(user.card)
    queryset = Order.objects.filter(card=user.card)
    start_date = request.GET.get('start_date', '')
    if start_date:
        date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        data_dict['start_time__gte'] = date
        data_dict['start_time__lte'] = date + datetime.timedelta(days=1)
    end_date = request.GET.get('end_date', '')
    if end_date:
        date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        data_dict['end_time__gte'] = date
        data_dict['end_time__lte'] = date + datetime.timedelta(days=1)
    select_status = request.GET.get('select_status', '')
    print(select_status)
    if select_status == '未完成':
        data_dict['status__gt'] = 1
    elif select_status == '已完成':
        data_dict['status__lt'] = 2
    queryset = queryset.filter(**data_dict).order_by('-status').order_by('-id')
    pagination = Pagination(request, queryset)
    page_queryset = pagination.page_queryset
    page_string = pagination.html()
    form = OrderModelForm()
    price_queryset = Price.objects.all()
    return render(request, 'user_order.html', locals())


def user_price_standard(request):
    queryset = Price.objects.all()



def user_message(request):
    """ 消息列表 """
    data_dict = {}
    user = Admin.objects.filter(id=request.session.get('info')['id']).first()
    queryset = Message.objects.filter(card=user.card)
    user_news = queryset.count()
    select_status = request.GET.get('select_status', '')
    print(select_status)
    if select_status == '未读':
        data_dict['user_is_read__gt'] = 1
    elif select_status == '已读':
        data_dict['user_is_read__lt'] = 2
    queryset = queryset.filter(**data_dict).order_by('-id')
    pagination = Pagination(request, queryset)
    page_queryset = pagination.page_queryset
    page_string = pagination.html()
    return render(request, 'user_message.html', locals())



def user_message_edit(request):
    """ 点击修改已读 """
    oid = request.GET.get('oid')
    # print(oid)
    Message.objects.filter(id=oid).update(user_is_read=1)
    return HttpResponse(json.dumps({'status': True}))


def user_allread(request):
    """ 全部已读 """
    id = request.session.get('info')['id']
    user_obj = Admin.objects.filter(id=id).first()
    Message.objects.filter(card=user_obj.card).update(user_is_read=1)
    return redirect('/user/message/')


def user_message_readcount(request):
    """ 未读消息条数 """
    user = Admin.objects.filter(id=request.session.get('info')['id']).first()
    queryset = Message.objects.filter(card=user.card)
    count = queryset.filter(user_is_read=2).count()
    # print(count)
    return HttpResponse(json.dumps({'status': True, 'data': count}))


def user_logout(request):
    """ 注销 """
    request.session.clear()
    return redirect('/admin/login/')


@csrf_exempt
def user_reset(request):
    """ 修改密码 """
    title = '修改密码'
    id = request.session.get('info')['id']
    user_obj = Admin.objects.filter(id=id).first()
    if request.method == 'GET':
        form = AdminModifyModelForm()
        return render(request, 'user_reset.html', locals())
    form = AdminModifyModelForm(data=request.POST, instance=user_obj)
    if form.is_valid():
        form.save()
        return HttpResponse(json.dumps({'status': True, 'error': '修改成功!'}))
    return HttpResponse(json.dumps({'status': False, 'error': form.errors}))
