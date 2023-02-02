import datetime

from django.shortcuts import render

from app.models import Order
from app.utils.pagination import Pagination


def record_list(request):
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
    search_data = request.GET.get('q', '')
    if search_data:
        data_dict['card__contains'] = search_data
    queryset = Order.objects.filter(**data_dict).order_by('-end_time')
    pagination = Pagination(request, queryset)
    page_queryset = pagination.page_queryset
    page_string = pagination.html()
    return render(request, 'record_list.html', locals())
