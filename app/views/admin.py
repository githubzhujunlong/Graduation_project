from io import BytesIO
import json

from django.core.exceptions import ValidationError
from django import forms
from django.core.validators import RegexValidator
from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from app.models import Admin
from app.utils.bootstrap import BootStrapModelForm, BootStrapForm
from app.utils.code import check_code
from app.utils.encrypt import md5
from app.utils.pagination import Pagination


def index_show(request):
    return render(request, 'layout.html')


class AdminModelForm(BootStrapModelForm):
    bootstrap_exclude_fields = ['avatar']
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
        fields = ['avatar', 'name', 'username', 'password', 'confirm_password', 'mobile']
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


def admin_list(request):
    data_dict = {}
    search_data = request.GET.get('q', '')
    if search_data:
        data_dict['name__contains'] = search_data
    queryset = Admin.objects.filter(**data_dict).order_by('type')
    pagination = Pagination(request, queryset)
    page_queryset = pagination.page_queryset
    page_string = pagination.html()
    return render(request, 'admin_list.html', locals())


def admin_register(request):
    """ 管理员注册 """
    title = '管理员注册'
    if request.method == 'GET':
        form = AdminModelForm()
        return render(request, 'admin_register.html', locals())
    form = AdminModelForm(data=request.POST, files=request.FILES)
    if form.is_valid():
        form.save()
        return redirect('/admin/list/')
    return render(request, 'admin_register.html', locals())


class LoginForm(BootStrapForm):
    username = forms.CharField(
        label='用户名',
        widget=forms.TextInput,
        # 默认表单字段不能为空
        required=True
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(render_value=True),
        required=True
    )
    code = forms.CharField(
        label='验证码',
        widget=forms.TextInput,
        required=True
    )

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        return md5(pwd)


def admin_login(request):
    """ 管理员/用户 登录 """
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'admin_login.html', locals())
    form = LoginForm(data=request.POST)
    if form.is_valid():
        # 验证码校验
        user_input_code = form.cleaned_data.pop('code')
        code = request.session.get('image_code', '')
        if code != '':
            del request.session['image_code']
        if code.upper() != user_input_code.upper():
            form.add_error('code', '验证码错误')
            return render(request, 'admin_login.html', locals())

        # 用户名密码校验
        obj = Admin.objects.filter(**form.cleaned_data).first()
        if not obj:
            form.add_error('password', '用户名或密码错误')
            return render(request, 'admin_login.html', locals())

        request.session['info'] = {
            'id': obj.id,
            'name': obj.username,
            'nickname': obj.name,
        }
        request.session.set_expiry(60 * 60 * 24 * 7)

        if obj.type == 1:
            return redirect('/finance/show/')
        else:
            return redirect('/user/order/')
    return render(request, 'admin_login.html', locals())


def image_code(request):
    """ 生成图片验证码 """
    img, code_string = check_code()
    request.session['image_code'] = code_string
    # 设置session时效60s
    request.session.set_expiry(60)
    stream = BytesIO()
    img.save(stream, 'png')
    return HttpResponse(stream.getvalue())
    # return HttpResponse(json.dumps({'status': True, 'data': stream.getvalue()}))


class AdminResetModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(render_value=True)
    )

    class Meta:
        model = Admin
        fields = ['username', 'password', 'confirm_password']
        widgets = {
            'password': forms.PasswordInput(render_value=True)
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        exists = Admin.objects.filter(username=username).exists()
        if not exists:
            raise ValidationError('该用户名不存在')
        return username

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        md5_pwd = md5(pwd)
        exists = Admin.objects.filter(id=self.instance.pk, password=md5_pwd).exists()
        if exists:
            raise ValidationError('密码不能与之前的一致')
        return md5_pwd

    def clean_confirm_password(self):
        # print(self.cleaned_data)
        # {'username': '111', 'password': '222', 'confirm_password': '333'}
        pwd = self.cleaned_data.get('password')
        confirm = md5(self.cleaned_data.get('confirm_password'))
        if confirm != pwd and pwd:
            raise ValidationError('密码不一致')
        # 返回的值就是要保存到数据库的值
        return confirm


def admin_forget(request):
    """ 忘记密码 """
    title = '忘记密码'
    if request.method == "GET":
        form = AdminResetModelForm()
        return render(request, 'admin_register.html', locals())
    username = request.POST['username']
    obj = Admin.objects.filter(username=username).first()
    form = AdminResetModelForm(data=request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return redirect('/admin/login/')
    return render(request, 'admin_register.html', locals())


def admin_logout(request):
    """ 注销 """
    request.session.clear()
    return redirect('/admin/login/')


class AdminEditModelForm(BootStrapModelForm):
    mobile = forms.CharField(
        label='手机号',
        validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误')],
    )

    class Meta:
        model = Admin
        fields = ['name', 'mobile']

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        exists = Admin.objects.filter(mobile=mobile).exclude(id=self.instance.pk).exists()
        if exists:
            raise ValidationError('手机号已存在')
        return mobile


def admin_info(request):
    id = request.session.get('info')['id']
    admin_obj = Admin.objects.filter(id=id).first()
    form = AdminEditModelForm()
    form2 = AdminEditAvatarModelForm()
    return render(request, 'admin_info.html', locals())


def admin_detail(request):
    id = request.session.get('info')['id']
    admin_dict = Admin.objects.filter(id=id).values('name', 'mobile').first()
    return HttpResponse(json.dumps({'status': True, 'data': admin_dict}))


@csrf_exempt
def admin_edit(request):
    id = request.session.get('info')['id']
    admin_obj = Admin.objects.filter(id=id).first()
    form = AdminEditModelForm(data=request.POST, instance=admin_obj)
    if form.is_valid():
        form.save()
        return HttpResponse(json.dumps({'status': True}))
    return HttpResponse(json.dumps({'status': False, 'error': form.errors}))


class AdminEditAvatarModelForm(BootStrapModelForm):
    bootstrap_exclude_fields = ['avatar']

    class Meta:
        model = Admin
        fields = ['avatar']


@csrf_exempt
def admin_edit_avatar(request):
    id = request.session.get('info')['id']
    admin_obj = Admin.objects.filter(id=id).first()
    print(request.FILES)
    form = AdminEditAvatarModelForm(files=request.FILES, instance=admin_obj)
    if form.is_valid():
        form.save()
        return HttpResponse(json.dumps({'status': True}))
    return HttpResponse(json.dumps({'status': False, 'error': form.errors}))


def admin_getAvatar(request):
    id = request.session.get('info')['id']
    admin_obj = Admin.objects.filter(id=id).first()
    # print(admin_obj.avatar.name, type(admin_obj.avatar.name))
    return HttpResponse(json.dumps({'data': admin_obj.avatar.name}))


# 修改和删除数据时，删除旧图片，保存新图
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver


# 删除时
@receiver(pre_delete, sender=Admin)
def avatar_delete(instance, **kwargs):
    print('进入文件删除方法，删的是', instance.avatar)
    instance.avatar.delete(False)


def admin_delete(request):
    id = request.session.get('info')['id']
    admin_obj = Admin.objects.filter(id=id)
    avatar_delete(admin_obj)
    admin_obj.delete()
    request.session.clear()
    return HttpResponse(json.dumps({'status': True}))


class AdminModifyModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(render_value=True)
    )

    class Meta:
        model = Admin
        fields = ['password', 'confirm_password']
        widgets = {
            'password': forms.PasswordInput(render_value=True)
        }

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        md5_pwd = md5(pwd)
        exists = Admin.objects.filter(id=self.instance.pk, password=md5_pwd).exists()
        if exists:
            raise ValidationError('密码不能与之前的一致')
        return md5_pwd

    def clean_confirm_password(self):
        # print(self.cleaned_data)
        # {'username': '111', 'password': '222', 'confirm_password': '333'}
        pwd = self.cleaned_data.get('password')
        confirm = md5(self.cleaned_data.get('confirm_password'))
        if confirm != pwd and pwd:
            raise ValidationError('密码不一致')
        # 返回的值就是要保存到数据库的值
        return confirm


@csrf_exempt
def admin_reset(request):
    """ 修改密码 """
    title = '修改密码'
    id = request.session.get('info')['id']
    admin_obj = Admin.objects.filter(id=id).first()
    if request.method == 'GET':
        form = AdminModifyModelForm()
        return render(request, 'admin_reset.html', locals())
    form = AdminModifyModelForm(data=request.POST, instance=admin_obj)
    if form.is_valid():
        form.save()
        return HttpResponse(json.dumps({'status': True, 'error': '修改成功!'}))
    return HttpResponse(json.dumps({'status': False, 'error': form.errors}))


def admin_user(request):
    id = request.session.get('info')['id']
    obj = Admin.objects.filter(id=id).first()
    if obj.type == 2:
        return redirect('/user/order/')
    else:
        return redirect('/finance/show/')
