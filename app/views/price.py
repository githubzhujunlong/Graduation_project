import json

from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from app.models import Price
from app.utils.pagination import Pagination
from app.utils.bootstrap import BootStrapModelForm


class PriceModelForm(BootStrapModelForm):
    class Meta:
        model = Price
        fields = '__all__'


def price_list(request):
    data_dict = {}
    search_data = request.GET.get('q', '')
    if search_data:
        data_dict['area__contains'] = search_data
    queryset = Price.objects.filter(**data_dict)
    pagination = Pagination(request, queryset)
    page_queryset = pagination.page_queryset
    page_string = pagination.html()
    form = PriceModelForm()
    return render(request, 'price_list.html', locals())


@csrf_exempt
def price_add(request):
    """ 新建区域定价 """
    form = PriceModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return HttpResponse(json.dumps({'status': True}))
    return HttpResponse(json.dumps({'status': False, 'error': form.errors}))


def price_delete(request):
    """ 删除区域定价 """
    uid = request.GET.get('uid')
    exists = Price.objects.filter(id=uid).exists()
    if not exists:
        return HttpResponse(json.dumps({'status': False, 'error': '删除失败,数据不存在'}))
    Price.objects.filter(id=uid).delete()
    return HttpResponse(json.dumps({'status': True}))


def price_detail(request):
    """ 编辑区域定价 """
    uid = request.GET.get('uid')
    # 返回值为字典
    price_dict = Price.objects.filter(id=uid).values('area', 'price').first()
    if not price_dict:
        return HttpResponse(json.dumps({'status': False, 'error': '您要修改的数据不存在'}))
    return HttpResponse(json.dumps({'status': True, 'data': price_dict}))


@csrf_exempt
def price_edit(request):
    """ 编辑区域定价 """
    uid = request.GET.get('uid')
    price_obj = Price.objects.filter(id=uid).first()
    if not price_obj:
        return HttpResponse(json.dumps({'status': False, 'error': '您要修改的数据不存在'}))
    form = PriceModelForm(data=request.POST, instance=price_obj)
    if form.is_valid():
        form.save()
        return HttpResponse(json.dumps({'status': True}))
    return HttpResponse(json.dumps({'status': False, 'error': form.errors}))
