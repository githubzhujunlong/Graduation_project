import datetime
import json

from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from app.models import Order, Park
from app.utils.bootstrap import BootStrapModelForm
from app.utils.pagination import Pagination


class OrderModelForm(BootStrapModelForm):
    class Meta:
        model = Order
        exclude = ['car_image', 'end_time', 'order_id', 'park_id']
        # fields = ['order_id']


def order_list(request):
    """ 订单列表 """
    data_dict = {}
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
    search_data = request.GET.get('q', '')
    if search_data:
        data_dict['card__contains'] = search_data
    queryset = Order.objects.filter(**data_dict).order_by('-status')
    pagination = Pagination(request, queryset)
    page_queryset = pagination.page_queryset
    page_string = pagination.html()
    form = OrderModelForm()
    return render(request, 'order_list.html', locals())


@csrf_exempt
def order_add(request):
    """ 新建订单 """
    request.POST._mutable = True
    list = request.POST['data'].split('&')
    del request.POST['data']
    # print(list)
    for i in range(len(list)):
        list[i] = list[i].split('=')
    # print(list)
    for item in list:
        request.POST[item[0]] = str(item[1])
        print(item[1], type(item[1]))
    # print(request.POST, request.FILES)
    form = OrderModelForm(data=request.POST, files=request.FILES)
    if form.is_valid():
        form.save()
        return HttpResponse(json.dumps({'status': True}))
    return HttpResponse(json.dumps({'status': False, 'error': form.errors}))
    # return HttpResponse('111')


# 修改和删除数据时，删除旧图片，保存新图
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver


# 删除时
@receiver(pre_delete, sender=Order)
def car_image_delete(instance, **kwargs):
    print('进入文件删除方法，删的是', instance.car_image)
    instance.car_image.delete(False)


def order_delete(request):
    """ 删除订单 """
    uid = request.GET.get('uid')
    exists = Order.objects.filter(id=uid).exists()
    if not exists:
        return HttpResponse(json.dumps({'status': False, 'error': '删除失败,数据不存在'}))
    order_obj = Order.objects.filter(id=uid).first()
    if order_obj.status == 2:
        Park.objects.filter(id=order_obj.park_id_id).update(park_status=2)
    car_image_delete(order_obj)
    Order.objects.filter(id=uid).delete()
    return HttpResponse(json.dumps({'status': True}))


def order_detail(request):
    """ 编辑订单 """
    uid = request.GET.get('uid')
    # 返回值为字典
    order_dict = Order.objects.filter(id=uid).values('park_id', 'price', 'card', 'order_id').first()
    if not order_dict:
        return HttpResponse(json.dumps({'status': False, 'error': '您要修改的数据不存在'}))
    return HttpResponse(json.dumps({'status': True, 'data': order_dict}))


@csrf_exempt
def order_edit(request):
    """ 编辑订单 """
    uid = request.GET.get('uid')
    order_obj = Order.objects.filter(id=uid).first()
    if not order_obj:
        return HttpResponse(json.dumps({'status': False, 'error': '您要修改的数据不存在'}))
    form = OrderModelForm(data=request.POST, instance=order_obj)
    if form.is_valid():
        form.save()
        return HttpResponse(json.dumps({'status': True}))
    return HttpResponse(json.dumps({'status': False, 'error': form.errors}))
