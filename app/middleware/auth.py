from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class AuthMiddleware(MiddlewareMixin):
    """ 中间件1 """

    def process_request(self, request):
        if request.path_info in [
            '/admin/login/',
            '/image/code/',
            '/admin/forget/',
            '/admin/register/',
            '/admin/logout/',
            '/user/register/',
            '/user/forget/',
            '/user/logout/',
        ]:
            return

        info_dict = request.session.get('info')
        if info_dict:
            return
        return redirect('/admin/login/')
