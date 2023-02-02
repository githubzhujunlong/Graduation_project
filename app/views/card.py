import json
import math
import os
import datetime
import random

from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from app.models import Order, Park, Price, Message
from app.utils.bootstrap import BootStrapModelForm
from app.utils.card.card import get_card
from app.views.order import car_image_delete


def card(request):
    """ 车牌识别 """
    return render(request, 'card.html')


@csrf_exempt
def card_identify(request):
    """ 仅识别 """
    card_obj = request.FILES.get('card_image')
    path = 'app/static/img/card/' + card_obj.name

    f = open(path, mode='wb')
    for chunk in card_obj.chunks():
        f.write(chunk)
    f.close()

    card_res = get_card(path, False)

    return HttpResponse(card_res)


@csrf_exempt
def card_identify_show(request):
    """ 处理过程 """
    card_obj = request.FILES.get('card_image')
    path = 'app/static/img/card/' + card_obj.name

    f = open(path, mode='wb')
    for chunk in card_obj.chunks():
        f.write(chunk)
    f.close()

    card_res = get_card(path, True)

    return HttpResponse(card_res)


class CardModelForm(BootStrapModelForm):
    class Meta:
        model = Order
        # exclude = ['car_image']
        fields = ['car_image']


@csrf_exempt
def card_submit(request):
    """ 提交车牌 """
    card_obj = request.FILES.get('car_image')
    path = 'app/static/img/card/' + card_obj.name

    f = open(path, mode='wb')
    for chunk in card_obj.chunks():
        f.write(chunk)
    f.close()

    card_res = get_card(path, False)
    select_card = Order.objects.filter(card=card_res).filter(status=2).first()

    if not select_card:
        free_park = Park.objects.filter(park_status=2)
        # print(len(free_park))

        if len(free_park) > 0:
            form = CardModelForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                form.instance.order_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + \
                                         str(random.randint(100000, 999999))
                form.instance.card = card_res
                form.instance.price = 0
                while True:
                    data = free_park.values('id')
                    length = len(data)
                    park_id_id = data[random.randint(0, length - 1)]['id']

                    park_status = free_park.filter(id=park_id_id).first().park_status
                    if park_status == 2:
                        form.instance.park_id_id = park_id_id
                        Park.objects.filter(id=park_id_id).update(park_status=1)
                        break
                form.save()
                Message.objects.create(
                    card=form.instance.card,
                    order_id=form.instance.order_id,
                    start_time=datetime.datetime.now(),
                    park_id_id=form.instance.park_id_id,
                    price=form.instance.price,
                )
                return HttpResponse(json.dumps({'status': True, 'type': 'in'}))
            return HttpResponse(json.dumps({'status': False, 'error': '上传的数据出问题了，请重试'}))
        else:
            return HttpResponse(json.dumps({'status': False, 'error': '车位已满'}))
    else:
        form = CardModelForm(data=request.POST, files=request.FILES, instance=select_card)
        form.instance.end_time = datetime.datetime.now()
        form.instance.status = 1
        form.instance.price = get_price(form.instance.order_id)
        car_image_delete(form.instance)

        Park.objects.filter(id=form.instance.park_id_id).update(park_status=2)
        form.save()
        Message.objects.create(
            card=form.instance.card,
            order_id=form.instance.order_id,
            start_time=form.instance.start_time,
            end_time=form.instance.end_time,
            park_id_id=form.instance.park_id_id,
            price=form.instance.price,
            status=1
        )
        return HttpResponse(json.dumps({'status': True, 'type': 'out'}))


card_res = ''


@csrf_exempt
def get_type(request):
    card_obj = request.FILES.get('car_image')
    path = 'app/static/img/card/' + card_obj.name

    f = open(path, mode='wb')
    for chunk in card_obj.chunks():
        f.write(chunk)
    f.close()

    global card_res
    card_res = get_card(path, False)
    select_card = Order.objects.filter(card=card_res).filter(status=2).first()
    if not select_card:
        return HttpResponse(json.dumps({'type': 'in'}))
    price = get_price(select_card.order_id)
    car_area = Park.objects.filter(id=select_card.park_id_id).first().park_id[0:1]
    park_price = Price.objects.filter(area=car_area).first().price

    return HttpResponse(json.dumps({'type': 'out',
                                    'price': price,
                                    'car_area': car_area,
                                    'park_price': park_price}))


@csrf_exempt
def car_in(request):
    free_park = Park.objects.filter(park_status=2)
    # print(len(free_park))

    if len(free_park) > 0:
        form = CardModelForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.instance.order_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + \
                                     str(random.randint(100000, 999999))
            global card_res
            form.instance.card = card_res
            form.instance.price = 0
            while True:
                data = free_park.values('id')
                length = len(data)
                park_id_id = data[random.randint(0, length - 1)]['id']

                park_status = free_park.filter(id=park_id_id).first().park_status
                if park_status == 2:
                    form.instance.park_id_id = park_id_id
                    Park.objects.filter(id=park_id_id).update(park_status=1)
                    break
            form.save()
            Message.objects.create(
                card=form.instance.card,
                order_id=form.instance.order_id,
                start_time=datetime.datetime.now(),
                park_id_id=form.instance.park_id_id,
                price=form.instance.price,
            )
            return HttpResponse(json.dumps({'status': True}))
        return HttpResponse(json.dumps({'status': False, 'error': '上传的数据出问题了，请重试'}))
    else:
        return HttpResponse(json.dumps({'status': False, 'error': '车位已满'}))


@csrf_exempt
def car_out(request):
    global card_res
    select_card = Order.objects.filter(card=card_res).filter(status=2).first()
    form = CardModelForm(data=request.POST, files=request.FILES, instance=select_card)
    form.instance.end_time = datetime.datetime.now()
    form.instance.status = 1
    form.instance.price = get_price(form.instance.order_id)
    car_image_delete(form.instance)

    Park.objects.filter(id=form.instance.park_id_id).update(park_status=2)
    form.save()
    Message.objects.create(
        card=form.instance.card,
        order_id=form.instance.order_id,
        start_time=form.instance.start_time,
        end_time=form.instance.end_time,
        park_id_id=form.instance.park_id_id,
        price=form.instance.price,
        status=1
    )
    return HttpResponse(json.dumps({'status': True}))


def get_price(order_id):
    order_obj = Order.objects.filter(order_id=order_id).first()
    area = order_obj.park_id.park_id[0]
    unit_price = Price.objects.filter(area=area).first().price
    start_time = order_obj.start_time
    end_time = datetime.datetime.now()

    price = 0
    date = datetime.datetime(start_time.year, start_time.month, start_time.day)
    if end_time > date + datetime.timedelta(days=1):
        if start_time <= datetime.datetime(start_time.year, start_time.month, start_time.day,
                                           8):
            seconds = (datetime.datetime(start_time.year, start_time.month, start_time.day,
                                         8) - start_time).seconds
            if seconds < 60 * 60:
                hours = 1
            else:
                hours = math.ceil(seconds / (60 * 60))
            price += hours * unit_price / 2
            seconds = (datetime.datetime(start_time.year,
                                         start_time.month,
                                         start_time.day,
                                         20) - datetime.datetime(start_time.year,
                                                                 start_time.month,
                                                                 start_time.day,
                                                                 8)).seconds
            if seconds < 60 * 60:
                hours = 1
            else:
                hours = math.ceil(seconds / (60 * 60))
            price += hours * unit_price
            seconds = ((date + datetime.timedelta(days=1)) - datetime.datetime(start_time.year,
                                                                               start_time.month,
                                                                               start_time.day,
                                                                               20)).seconds
            if seconds < 60 * 60:
                hours = 1
            else:
                hours = math.ceil(seconds / (60 * 60))
            price += hours * unit_price / 2
        elif datetime.datetime(start_time.year,
                               start_time.month,
                               start_time.day,
                               8) < start_time < datetime.datetime(start_time.year,
                                                                   start_time.month,
                                                                   start_time.day,
                                                                   20):
            seconds = (datetime.datetime(start_time.year,
                                         start_time.month,
                                         start_time.day,
                                         20) - start_time).seconds
            if seconds < 60 * 60:
                hours = 1
            else:
                hours = math.ceil(seconds / (60 * 60))
            price += hours * unit_price
            seconds = ((date + datetime.timedelta(days=1)) - datetime.datetime(start_time.year,
                                                                               start_time.month,
                                                                               start_time.day,
                                                                               20)).seconds
            if seconds < 60 * 60:
                hours = 1
            else:
                hours = math.ceil(seconds / (60 * 60))
            price += hours * unit_price / 2
        else:
            seconds = ((date + datetime.timedelta(days=1)) - start_time).seconds
            if seconds < 60 * 60:
                hours = 1
            else:
                hours = math.ceil(seconds / (60 * 60))
            price += hours * unit_price / 2
        date += datetime.timedelta(days=1)
        while end_time > date + datetime.timedelta(days=1):
            price += 24 * unit_price * 3 / 4
            date += datetime.timedelta(days=1)

        if end_time <= datetime.datetime(end_time.year, end_time.month, end_time.day,
                                         8):
            seconds = (end_time - date).seconds
            if seconds < 60 * 60:
                hours = 1
            else:
                hours = math.ceil(seconds / (60 * 60))
            price += hours * unit_price / 2
        elif datetime.datetime(end_time.year,
                               end_time.month,
                               end_time.day,
                               8) < end_time < datetime.datetime(end_time.year,
                                                                 end_time.month,
                                                                 end_time.day,
                                                                 20):
            seconds = (datetime.datetime(end_time.year, end_time.month, end_time.day,
                                         8) - date).seconds
            if seconds < 60 * 60:
                hours = 1
            else:
                hours = math.ceil(seconds / (60 * 60))
            price += hours * unit_price / 2

            seconds = (end_time - datetime.datetime(end_time.year,
                                                    end_time.month,
                                                    end_time.day,
                                                    8)).seconds
            if seconds < 60 * 60:
                hours = 1
            else:
                hours = math.ceil(seconds / (60 * 60))
            price += hours * unit_price
        else:
            seconds = (datetime.datetime(end_time.year, end_time.month, end_time.day,
                                         8) - date).seconds
            if seconds < 60 * 60:
                hours = 1
            else:
                hours = math.ceil(seconds / (60 * 60))
            price += hours * unit_price / 2

            seconds = (datetime.datetime(start_time.year,
                                         start_time.month,
                                         start_time.day,
                                         20) - datetime.datetime(end_time.year,
                                                                 end_time.month,
                                                                 end_time.day,
                                                                 8)).seconds
            if seconds < 60 * 60:
                hours = 1
            else:
                hours = math.ceil(seconds / (60 * 60))
            price += hours * unit_price
            seconds = (end_time - datetime.datetime(start_time.year,
                                                    start_time.month,
                                                    start_time.day,
                                                    20)).seconds
            if seconds < 60 * 60:
                hours = 1
            else:
                hours = math.ceil(seconds / (60 * 60))
            price += hours * unit_price / 2

    if end_time < datetime.datetime(start_time.year, start_time.month, start_time.day) + datetime.timedelta(days=1):
        if end_time <= datetime.datetime(end_time.year, end_time.month, end_time.day,
                                         8):
            seconds = (end_time - start_time).seconds
            if seconds < 60 * 60:
                hours = 1
            else:
                hours = math.ceil(seconds / (60 * 60))
            price += hours * unit_price / 2
        elif datetime.datetime(end_time.year,
                               end_time.month,
                               end_time.day,
                               8) < end_time < datetime.datetime(end_time.year,
                                                                 end_time.month,
                                                                 end_time.day,
                                                                 20):
            if start_time < datetime.datetime(end_time.year,
                                              end_time.month,
                                              end_time.day,
                                              8):
                seconds = (datetime.datetime(end_time.year, end_time.month, end_time.day,
                                             8) - start_time).seconds
                if seconds < 60 * 60:
                    hours = 1
                else:
                    hours = math.ceil(seconds / (60 * 60))
                price += hours * unit_price / 2
                seconds = (end_time - datetime.datetime(end_time.year, end_time.month, end_time.day,
                                                        8)).seconds
                if seconds < 60 * 60:
                    hours = 1
                else:
                    hours = math.ceil(seconds / (60 * 60))
                price += hours * unit_price
            else:
                seconds = (end_time - start_time).seconds
                if seconds < 60 * 60:
                    hours = 1
                else:
                    hours = math.ceil(seconds / (60 * 60))
                price += hours * unit_price

        else:
            if start_time < datetime.datetime(end_time.year,
                                              end_time.month,
                                              end_time.day,
                                              8):
                seconds = (datetime.datetime(end_time.year, end_time.month, end_time.day,
                                             8) - start_time).seconds
                if seconds < 60 * 60:
                    hours = 1
                else:
                    hours = math.ceil(seconds / (60 * 60))
                price += hours * unit_price / 2
                seconds = (datetime.datetime(end_time.year, end_time.month, end_time.day,
                                             20) - datetime.datetime(end_time.year, end_time.month, end_time.day,
                                                                     8)).seconds
                if seconds < 60 * 60:
                    hours = 1
                else:
                    hours = math.ceil(seconds / (60 * 60))
                price += hours * unit_price
                seconds = (end_time - datetime.datetime(end_time.year, end_time.month, end_time.day,
                                                        20)).seconds
                if seconds < 60 * 60:
                    hours = 1
                else:
                    hours = math.ceil(seconds / (60 * 60))
                price += hours * unit_price / 2

            elif datetime.datetime(start_time.year,
                                   start_time.month,
                                   start_time.day,
                                   8) < start_time < datetime.datetime(start_time.year,
                                                                       start_time.month,
                                                                       start_time.day,
                                                                       20):
                seconds = (datetime.datetime(start_time.year,
                                             start_time.month,
                                             start_time.day,
                                             20) - start_time).seconds
                if seconds < 60 * 60:
                    hours = 1
                else:
                    hours = math.ceil(seconds / (60 * 60))
                price += hours * unit_price
                seconds = (end_time - datetime.datetime(start_time.year,
                                                        start_time.month,
                                                        start_time.day,
                                                        20)).seconds
                if seconds < 60 * 60:
                    hours = 1
                else:
                    hours = math.ceil(seconds / (60 * 60))
                price += hours * unit_price / 2

            else:
                seconds = (end_time - start_time).seconds
                if seconds < 60 * 60:
                    hours = 1
                else:
                    hours = math.ceil(seconds / (60 * 60))
                price += hours * unit_price / 2

    return float(price)


# print(price)
# print(area, unit_price)
# return HttpResponse('1111')


def modify_price(request):
    query_set = Order.objects.filter(status=2)
    price_list = []
    for obj in query_set:
        Order.objects.filter(order_id=obj.order_id).update(price=get_price(obj.order_id))
        price_list.append({'oid': obj.order_id, 'price': get_price(obj.order_id)})
    # print(price_list)
    return HttpResponse(json.dumps({'status': True, 'data': price_list}))
    # print('modify被执行了')
    # return HttpResponse('111')
