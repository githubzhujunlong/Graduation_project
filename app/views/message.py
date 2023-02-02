import json

from django.shortcuts import render, HttpResponse, redirect

from app.models import Message, Admin
from app.utils.pagination import Pagination


def message_list(request):
    """ 消息列表 """
    data_dict = {}
    select_status = request.GET.get('select_status', '')
    print(select_status)
    if select_status == '未读':
        data_dict['is_read__gt'] = 1
    elif select_status == '已读':
        data_dict['is_read__lt'] = 2
    queryset = Message.objects.filter(**data_dict).order_by('-id')
    pagination = Pagination(request, queryset)
    page_queryset = pagination.page_queryset
    page_string = pagination.html()
    return render(request, 'message_list.html', locals())


def message_edit(request):
    """ 点击修改已读 """
    oid = request.GET.get('oid')
    # print(oid)
    Message.objects.filter(id=oid).update(is_read=1)
    return HttpResponse(json.dumps({'status': True}))


def admin_allread(request):
    """ 全部已读 """
    Message.objects.all().update(is_read=1)
    return redirect('/message/list/')


def read_count(request):
    """ 未读消息条数 """
    count = Message.objects.filter(is_read=2).count()
    # print(count)
    return HttpResponse(json.dumps({'status': True, 'data': count}))
