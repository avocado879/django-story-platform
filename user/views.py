from django.contrib.auth import login as auth_login, logout as auth_logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .models import CustomerUser, PasswordResetCode


def logout(request):
    auth_logout(request)
    return redirect(to='/story_app/index/')


def register(request):
    """
    注册业务：
    1.获取请求参数
    2.业务处理
    3.结果响应
    """
    if request.method == "GET":
        return render(request, "register.html")
    elif request.method == "POST":
        # 2.1 获取请求参数
        username = request.POST.get("username")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        # 2.2 比对用户名
        customeruser = CustomerUser.objects.filter(username=username).first()
        if customeruser:
            return render(request, "register.html", {'msg': '用户名已存在，请直接登录'})

        # 2.3 比对密码
        elif password != password2:
            return render(request, "register.html", {'msg': '两次密码不匹配'})

        # 2.4 密码长度验证
        elif len(password) < 4:
            return render(request, "register.html", {'msg': '密码长度至少为4位'})

        else:
            # 创建用户，默认为普通用户角色
            user = CustomerUser.objects.create_user(
                username=username,
                password=password,
                role='user'  # 默认角色为普通用户
            )

            # 自动登录
            auth_login(request, user)
            return redirect(to='/stories/index/')

def logins(request):
    """
    用户登录：
    1.登录页---GET
    2.进行登录---POST
    """
    if request.method == "GET":
        return render(request, 'login.html')  # 使用完整路径
    else:
        # 登录逻辑
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 基本验证
        if not username or not password:
            return render(request, 'login.html', {'msg': '请输入用户名和密码'})

        # 查询用户
        user = CustomerUser.objects.filter(username=username).first()
        if user:
            # 验证密码
            if user.check_password(password):
                # 使用内置login函数创建会话
                auth_login(request, user)

                # 根据角色跳转到不同页面（可选）
                if user.role == 'admin' or user.is_superuser:
                    # 管理员可以跳转到管理页面或其他特定页面
                    return redirect('/admin/')
                else:
                    # 普通用户跳转到首页
                    return redirect('/stories/')
            else:
                msg = '密码不正确'
        else:
            msg = '用户名不存在'

        return render(request, 'login.html', {'msg': msg})
# def logins(request):
#     """
#     用户登录：
#     1.登录页---GET
#     2.进行登录---POST
#     """
#     if request.method == "GET":
#         return render(request, 'login.html')
#     else:
#         # 登录逻辑
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#
#         # 基本验证
#         if not username or not password:
#             return render(request, 'login.html', {'msg': '请输入用户名和密码'})
#
#         # 查询用户
#         user = CustomerUser.objects.filter(username=username).first()
#         if user:
#             # 验证密码
#             if user.check_password(password):
#                 # 使用内置login函数创建会话
#                 auth_login(request, user)
#
#                 # 根据角色跳转到不同页面（可选）
#                 if user.role == 'admin' or user.is_superuser:
#                     # 管理员可以跳转到管理页面或其他特定页面
#                     return redirect('/admin')
#                 else:
#                     # 普通用户跳转到首页
#                     return redirect('/stories/index/')
#             else:
#                 msg = '密码不正确'
#         else:
#             msg = '用户名不存在'
#
#         return render(request, 'login.html', {'msg': msg})


# 忘记密码页面
def forgot_password(request):
    """
    显示忘记密码页面
    """
    if request.method == "GET":
        return render(request, 'forgot_password.html')


# 发送邮箱验证码
@csrf_exempt
def send_verify_code(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        if not email:
            return JsonResponse({'success': False, 'message': '请输入邮箱地址'})

        # 检查邮箱是否已注册
        if not CustomerUser.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': '该邮箱未注册'})

        # 生成并保存验证码
        reset_code = PasswordResetCode.generate_code(email)

        # 发送邮件
        try:
            email_sent = send_verification_email(email, reset_code.code)

            if email_sent:
                return JsonResponse({'success': True, 'message': '验证码已发送到您的邮箱'})
            else:
                # 如果邮件发送失败，删除验证码记录
                reset_code.delete()
                return JsonResponse({'success': False, 'message': '邮件发送失败，请稍后重试'})

        except Exception as e:
            # 如果出现异常，删除验证码记录
            reset_code.delete()
            return JsonResponse({'success': False, 'message': f'邮件发送失败: {str(e)}'})

    return JsonResponse({'success': False, 'message': '请求方法错误'})


def send_verification_email(email, verification_code):
    """
    使用QQ邮箱发送验证码邮件
    """
    try:
        subject = '密码重置验证码'
        message = f"""
        您好！

        您正在尝试重置密码，您的验证码是：{verification_code}

        验证码有效期为5分钟，请尽快使用。

        如果这不是您本人的操作，请忽略此邮件。

        谢谢！
        """

        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )

        print(f"验证码邮件发送成功 - 收件人: {email}, 验证码: {verification_code}")
        return True

    except Exception as e:
        print(f"QQ邮箱发送失败: {e}")
        return False


# 重置密码
@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        code = request.POST.get('verify_code', '').strip()
        new_password = request.POST.get('new_password', '')
        confirm_new_password = request.POST.get('confirm_new_password', '')

        # 验证输入
        if not all([email, code, new_password, confirm_new_password]):
            return render(request, 'forgot_password.html', {
                'error_message': '请填写所有字段'
            })

        # 验证密码一致性
        if new_password != confirm_new_password:
            return render(request, 'forgot_password.html', {
                'error_message': '两次输入的密码不一致'
            })

        # 验证密码长度
        if len(new_password) < 4 or len(new_password) > 20:
            return render(request, 'forgot_password.html', {
                'error_message': '密码长度必须在4-20个字符之间'
            })

        # 验证验证码
        try:
            reset_code = PasswordResetCode.objects.filter(
                email=email,
                code=code,
                is_used=False
            ).latest('created_at')

            if reset_code.is_expired():
                return render(request, 'forgot_password.html', {
                    'error_message': '验证码已过期，请重新获取'
                })

            # 验证码正确，重置密码
            user = CustomerUser.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            # 标记验证码为已使用
            reset_code.is_used = True
            reset_code.save()

            return render(request, 'forgot_password.html', {
                'success_message': '密码重置成功！请使用新密码登录。'
            })

        except PasswordResetCode.DoesNotExist:
            return render(request, 'forgot_password.html', {
                'error_message': '验证码错误或已使用'
            })
        except CustomerUser.DoesNotExist:
            return render(request, 'forgot_password.html', {
                'error_message': '用户不存在'
            })

    return render(request, 'forgot_password.html', {
        'error_message': '请求方法错误'
    })