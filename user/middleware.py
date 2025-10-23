# middleware.py
from django.shortcuts import redirect


class SimpleLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        print(f"=== 中间件调试 ===")
        print(f"路径: {path}")
        print(f"用户: {request.user}")
        print(f"认证状态: {request.user.is_authenticated}")

        # 不需要登录的路径
        public_paths = [
            '/user/login/',
            '/user/register/',
            '/user/forgot_password/',
            '/user/send_verify_code/',
            '/user/reset_password/',
            '/stories/index/',
            '/user/admin_dashboard/',
            '/user/check_permission/',
            '/user/dashboard/',
            '/user/admin_users/',
            '/user/admin_stories/'
            '/user/admin_categories/',
            '/',
        ]

        # 静态文件直接放行
        if path.startswith('/static/') or path.startswith('/media/'):
            return self.get_response(request)

        # Django admin 直接放行
        if path.startswith('/admin/'):
            return self.get_response(request)

        # 公共路径直接放行
        if path in public_paths:
            return self.get_response(request)

        # 检查用户认证
        if not request.user.is_authenticated:
            print("用户未认证，重定向到登录页面")
            return redirect('/user/login/')

        print("用户已认证，放行")
        return self.get_response(request)