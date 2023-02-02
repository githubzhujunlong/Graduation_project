"""graduation_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve

from app.views import admin, index, park, price, card, order, record, finance, message, user

urlpatterns = [

    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}, name='media'),
    path('', admin.admin_user),

    # 管理员
    path('admin/list/', admin.admin_list),
    path('admin/register/', admin.admin_register),
    path('admin/login/', admin.admin_login),
    path('admin/forget/', admin.admin_forget),
    path('image/code/', admin.image_code),
    path('admin/logout/', admin.admin_logout),
    path('admin/info/', admin.admin_info),
    path('admin/edit/', admin.admin_edit),
    path('admin/detail/', admin.admin_detail),
    path('admin/delete/', admin.admin_delete),
    path('admin/reset/', admin.admin_reset),
    path('admin/edit/avatar/', admin.admin_edit_avatar),
    path('admin/getAvatar/', admin.admin_getAvatar),

    # 车位
    path('park/list/', park.park_list),
    path('park/add/', park.park_add),
    path('park/delete/', park.park_delete),
    path('park/edit/', park.park_edit),
    path('park/detail/', park.park_detail),

    # 价格调整
    path('price/list/', price.price_list),
    path('price/add/', price.price_add),
    path('price/delete/', price.price_delete),
    path('price/edit/', price.price_edit),
    path('price/detail/', price.price_detail),

    # 车牌识别
    path('card/', card.card),
    path('card/identify/', card.card_identify),
    path('card/identify/show/', card.card_identify_show),
    path('card/submit/', card.card_submit),
    path('get/price/', card.get_price),
    path('card/modifyprice/', card.modify_price),
    path('get/type/', card.get_type),
    path('car/in/', card.car_in),
    path('car/out/', card.car_out),

    # 订单管理
    path('order/list/', order.order_list),
    path('order/add/', order.order_add),
    path('order/delete/', order.order_delete),
    path('order/edit/', order.order_edit),
    path('order/detail/', order.order_detail),

    # 出入记录
    path('record/list/', record.record_list),

    # 财务管理
    path('finance/show/', finance.finance_show),
    path('finance/order/', finance.finance_order),
    path('finance/price/', finance.finance_price),
    path('finance/order/count/', finance.finance_order_count),

    # 系统消息
    path('message/list/', message.message_list),
    path('message/edit/', message.message_edit),
    path('message/read/count/', message.read_count),
    path('admin/all/read/', message.admin_allread),

    # 用户
    path('user/register/', user.user_register),
    path('user/show/', user.user_show),
    path('user/info/', user.user_info),
    path('user/delete/', user.user_delete),
    path('user/edit/', user.user_edit),
    path('user/detail/', user.user_detail),
    path('user/order/', user.user_order),
    path('user/message/', user.user_message),
    path('user/message/edit/', user.user_message_edit),
    path('user/message/readcount/', user.user_message_readcount),
    path('user/logout/', user.user_logout),
    path('user/reset/', user.user_reset),
    path('user/all/read/', user.user_allread),
    path('user/edit/avatar/', user.user_edit_avatar),
    path('user/getAvatar/', user.user_getAvatar),
]
