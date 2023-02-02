import datetime
import json

from django.db.models import Sum
from django.shortcuts import render, HttpResponse

from app.models import Order, Park


def finance_show(request):
    return render(request, 'finance_show.html')


def finance_order(request):
    date = datetime.datetime.now()
    today = datetime.datetime(year=date.year, month=date.month, day=date.day)
    day_list = [
        (today - datetime.timedelta(days=6)).day,
        (today - datetime.timedelta(days=5)).day,
        (today - datetime.timedelta(days=4)).day,
        (today - datetime.timedelta(days=3)).day,
        (today - datetime.timedelta(days=2)).day,
        (today - datetime.timedelta(days=1)).day,
        (today).day,
    ]
    # print(day_list)
    count_list = []
    for day in day_list:
        count_list.append(Order.objects.filter(start_time__day=day).count())
    count_list1 = []
    for day in day_list:
        count_list1.append(Order.objects.filter(end_time__day=day).filter(status=1).count())
    # print(count_list)

    legend = ['当日驶入车辆数', '当日驶出车辆数']
    series_list = [
        {
            'name': '当日驶入车辆数',
            'type': 'bar',
            'data': count_list,
        },
        {
            'name': '当日驶出车辆数',
            'type': 'bar',
            'data': count_list1,
        },
    ]
    x_axis = day_list

    res = {
        'status': True,
        'data': {
            'legend': legend,
            'series_list': series_list,
            'x_axis': x_axis,
        }
    }

    return HttpResponse(json.dumps(res))


def finance_price(request):
    date = datetime.datetime.now()
    today = datetime.datetime(year=date.year, month=date.month, day=date.day)
    day_list = [
        (today - datetime.timedelta(days=6)).day,
        (today - datetime.timedelta(days=5)).day,
        (today - datetime.timedelta(days=4)).day,
        (today - datetime.timedelta(days=3)).day,
        (today - datetime.timedelta(days=2)).day,
        (today - datetime.timedelta(days=1)).day,
        (today).day,
    ]
    # print(day_list)
    count_list = []
    for day in day_list:
        if Order.objects.filter(end_time__day=day):
            count_list.append(Order.objects.filter(end_time__day=day).aggregate(sum_price=Sum('price'))['sum_price'])
        else:
            count_list.append(0)
    # print(count_list)

    legend = ['收入金额']
    series_list = [
        {
            'name': '收入金额',
            'type': 'line',
            "stack": 'Total',
            'data': count_list,
        },
    ]
    x_axis = day_list

    res = {
        'status': True,
        'data': {
            'legend': legend,
            'series_list': series_list,
            'x_axis': x_axis,
        }
    }

    return HttpResponse(json.dumps(res))
    # return HttpResponse('111')


def finance_order_count(request):
    all_order = Order.objects.all().count()
    undone_order = Order.objects.filter(status=2).count()
    all_price = Order.objects.filter(status=1).aggregate(all_price=Sum('price'))
    today_price = Order.objects.filter(end_time__day=datetime.datetime.now().day).filter(status=1).aggregate(
        today_price=Sum('price'))
    all_park = Park.objects.all().count()
    free_park = Park.objects.filter(park_status=2).count()
    res = {
        'status': True,
        'data': {
            'all_order': all_order,
            'undone_order': undone_order,
            'all_price': all_price,
            'today_price': today_price,
            'all_park': all_park,
            'free_park': free_park,
        }
    }

    # print(res)
    return HttpResponse(json.dumps(res))
