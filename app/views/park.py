import json

from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from app.models import Park, Order
from app.utils.pagination import Pagination
from app.utils.bootstrap import BootStrapModelForm


class ParkModelForm(BootStrapModelForm):
    class Meta:
        model = Park
        fields = '__all__'


def park_list(request):
    for obj in Park.objects.filter(park_status=1):
        if Order.objects.filter(status=2).filter(park_id_id=obj.id):
            continue
        else:
            Park.objects.filter(id=obj.id).update(park_status=2)
    data_dict = {}
    select_status = request.GET.get('select_status', '')
    if select_status == '未占用':
        data_dict['park_status__gt'] = 1
    elif select_status == '已占用':
        data_dict['park_status__lt'] = 2
    search_data = request.GET.get('q', '')
    if search_data:
        data_dict['park_id__contains'] = search_data.upper()
    queryset = Park.objects.filter(**data_dict)
    pagination = Pagination(request, queryset)
    page_queryset = pagination.page_queryset
    page_string = pagination.html()
    form = ParkModelForm()
    return render(request, 'park_list.html', locals())


@csrf_exempt
def park_add(request):
    """ 新建车位 """
    form = ParkModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return HttpResponse(json.dumps({'status': True}))
    return HttpResponse(json.dumps({'status': False, 'error': form.errors}))


def park_delete(request):
    """ 删除订单 """
    uid = request.GET.get('uid')
    exists = Park.objects.filter(id=uid).exists()
    if not exists:
        return HttpResponse(json.dumps({'status': False, 'error': '删除失败,数据不存在'}))
    Park.objects.filter(id=uid).delete()
    return HttpResponse(json.dumps({'status': True}))


def park_detail(request):
    """ 编辑订单 """
    uid = request.GET.get('uid')
    # 返回值为字典
    park_dict = Park.objects.filter(id=uid).values('park_id', 'park_status').first()
    if not park_dict:
        return HttpResponse(json.dumps({'status': False, 'error': '您要修改的数据不存在'}))
    return HttpResponse(json.dumps({'status': True, 'data': park_dict}))


@csrf_exempt
def park_edit(request):
    """ 编辑订单 """
    uid = request.GET.get('uid')
    park_obj = Park.objects.filter(id=uid).first()
    if not park_obj:
        return HttpResponse(json.dumps({'status': False, 'error': '您要修改的数据不存在'}))
    form = ParkModelForm(data=request.POST, instance=park_obj)
    if form.is_valid():
        form.save()
        return HttpResponse(json.dumps({'status': True}))
    return HttpResponse(json.dumps({'status': False, 'error': form.errors}))
