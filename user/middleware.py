from django.shortcuts import redirect


class MyMiddlewareA(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 请求前逻辑
        print('MyMiddlewareA----------------------请求前。。。。。。。。。。')
        response = self.get_response(request)
        # 响应后逻辑
        print('MyMiddlewareA----------------------响应后。。。。。。。。。。')
        return response


class MyMiddlewareB(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 请求前逻辑
        print('MyMiddlewareB----------------------请求前。。。。。。。。。。')
        response = self.get_response(request)
        # 响应后逻辑
        print('MyMiddlewareB----------------------响应后。。。。。。。。。。')
        return response


class LoginMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 请求前逻辑
        print('LoginMiddleware----------------------请求前。。。。。。。。。。')
        # 获取请求路径
        path = request.path
        print(f"请求路径: {path}")

        # 允许访问的路径列表（不需要登录）
        allowed_paths = [
            '/user/register/',
            '/user/login/',
            '/story_app/index/',
            '/admin/',  # 添加admin路径
            '/admin/login/',  # 添加admin登录路径
        ]

        # 判断是否放行
        if (request.user.is_authenticated or
                path in allowed_paths or
                path.startswith('/admin/') or  # 允许所有admin路径
                path.startswith('/static/') or  # 允许静态文件
                path.startswith('/media/')):  # 允许媒体文件

            response = self.get_response(request)
            # 响应后逻辑
            print('LoginMiddleware----------------------响应后。。。。。。。。。。')
            return response
        else:
            print(f"重定向到登录页面: {path}")
            return redirect('/user/login/')