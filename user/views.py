import json
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import CustomerUser, PasswordResetCode
from stories.models import Story, Comment
from django.views.decorators.http import require_http_methods, require_POST
from .utils import oss_client
from .utils import api_mixin  # 新增导入

def logout(request):
    auth_logout(request)
    return redirect(to='/stories/index/')


def register(request):
    """
    注册业务：支持 API 调用
    """
    if request.method == "GET":
        context = {'message': '用户注册页面'}

        # 如果是 API 请求，返回 JSON
        if request.GET.get('format') == 'json' or request.headers.get('Accept') == 'application/json':
            return api_mixin.render_to_api_response(context)

        return render(request, "register.html")
    elif request.method == "POST":
        # 从不同来源获取参数
        if request.headers.get('Content-Type') == 'application/json':
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
            password2 = data.get("password2")
            email = data.get("email", "")
        else:
            username = request.POST.get("username")
            password = request.POST.get("password")
            password2 = request.POST.get("password2")
            email = request.POST.get("email", "")

        # 验证用户名
        customeruser = CustomerUser.objects.filter(username=username).first()
        if customeruser:
            error_msg = '用户名已存在，请直接登录'
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'message': error_msg})
            return render(request, "register.html", {'msg': error_msg})

        # 验证密码
        elif password != password2:
            error_msg = '两次密码不匹配'
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'message': error_msg})
            return render(request, "register.html", {'msg': error_msg})

        # 密码长度验证
        elif len(password) < 4:
            error_msg = '密码长度至少为4位'
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'message': error_msg})
            return render(request, "register.html", {'msg': error_msg})

        else:
            # 创建用户，默认为普通用户角色
            user = CustomerUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                role='user'  # 默认角色为普通用户
            )

            # 自动登录
            auth_login(request, user)

            # API 响应
            if request.headers.get('Content-Type') == 'application/json':
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'avatar_url': user.get_avatar_url()
                }
                return JsonResponse({
                    'success': True,
                    'message': '注册成功',
                    'user': user_data
                })

            return redirect(to='/stories/index/')
# def register(request):
#     """
#     注册业务：
#     1.获取请求参数
#     2.业务处理
#     3.结果响应
#     """
#     if request.method == "GET":
#         return render(request, "register.html")
#     elif request.method == "POST":
#         # 2.1 获取请求参数
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         password2 = request.POST.get("password2")
#
#         # 2.2 比对用户名
#         customeruser = CustomerUser.objects.filter(username=username).first()
#         if customeruser:
#             return render(request, "register.html", {'msg': '用户名已存在，请直接登录'})
#
#         # 2.3 比对密码
#         elif password != password2:
#             return render(request, "register.html", {'msg': '两次密码不匹配'})
#
#         # 2.4 密码长度验证
#         elif len(password) < 4:
#             return render(request, "register.html", {'msg': '密码长度至少为4位'})
#
#         else:
#             # 创建用户，默认为普通用户角色
#             user = CustomerUser.objects.create_user(
#                 username=username,
#                 password=password,
#                 role='user'  # 默认角色为普通用户
#             )
#
#             # 自动登录
#             auth_login(request, user)
#             return redirect(to='/stories/index/')


def logins(request):
    """
    用户登录：支持 API 调用
    """
    if request.method == "GET":
        context = {'message': '用户登录页面'}

        # 如果是 API 请求，返回 JSON
        if request.GET.get('format') == 'json' or request.headers.get('Accept') == 'application/json':
            return api_mixin.render_to_api_response(context)

        return render(request, 'login.html')
    else:
        # 登录逻辑
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 如果是 JSON 请求，从请求体中获取数据
        if request.headers.get('Content-Type') == 'application/json':
            try:
                data = json.loads(request.body)
                username = data.get('username')
                password = data.get('password')
            except:
                pass

        # 基本验证
        if not username or not password:
            error_msg = '请输入用户名和密码'
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'message': error_msg})
            return render(request, 'login.html', {'msg': error_msg})

        # 查询用户
        user = CustomerUser.objects.filter(username=username).first()
        if user:
            # 验证密码
            if user.check_password(password):
                # 使用内置login函数创建会话
                auth_login(request, user)

                # API 响应
                if request.headers.get('Content-Type') == 'application/json':
                    user_data = {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': user.role,
                        'is_staff': user.is_staff,
                        'avatar_url': user.get_avatar_url()
                    }
                    return JsonResponse({
                        'success': True,
                        'message': '登录成功',
                        'user': user_data
                    })

                # 根据角色跳转到不同页面
                if user.is_staff or user.is_superuser:
                    return redirect('/user/admin_dashboard/')
                else:
                    return redirect('/stories/index/')
            else:
                msg = '密码不正确'
        else:
            msg = '用户名不存在'

        # API 错误响应
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'message': msg})

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
#                 # 根据角色跳转到不同页面（可选）
#                 # if user.role == 'admin' or user.is_superuser:
#                 if user.is_staff or user.is_superuser:
#                     # 管理员可以跳转到管理页面或其他特定页面
#                     return redirect('/user/admin_dashboard/')
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


@login_required
def profile_view(request):
    """个人中心页面 - 支持 API"""
    user = request.user
    # 获取用户的故事和评论
    user_stories = Story.objects.filter(author=user).order_by('-created_at')
    user_comments = Comment.objects.filter(author=user).order_by('-created_at')

    context = {
        'user': user,
        'user_stories': user_stories,
        'user_comments': user_comments,
    }

    # 如果是 API 请求，返回 JSON
    if request.GET.get('format') == 'json' or request.headers.get('Accept') == 'application/json':
        # 构建用户数据
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'pen_name': user.pen_name,
            'bio': user.bio,
            'avatar_url': user.get_avatar_url(),
            'role': user.role,
            'created_at': user.created_at.isoformat(),
            'notify_comments': user.notify_comments,
            'notify_likes': user.notify_likes
        }

        # 构建故事数据
        stories_data = []
        for story in user_stories:
            stories_data.append({
                'id': story.id,
                'title': story.title,
                'content': story.content[:200] + '...' if len(story.content) > 200 else story.content,
                'category': story.category.name if story.category else '未分类',
                'status': story.status,
                'likes': story.likes,
                'created_at': story.created_at.isoformat()
            })

        # 构建评论数据
        comments_data = []
        for comment in user_comments:
            comments_data.append({
                'id': comment.id,
                'content': comment.content,
                'story_id': comment.story.id,
                'story_title': comment.story.title,
                'likes': comment.likes,
                'created_at': comment.created_at.isoformat()
            })

        return JsonResponse({
            'success': True,
            'user': user_data,
            'stories': stories_data,
            'comments': comments_data,
            'stories_count': len(stories_data),
            'comments_count': len(comments_data)
        })

    return render(request, 'profile.html', context)
@login_required
# def profile_view(request):
#     """个人中心页面"""
#     user = request.user
#     # 获取用户的故事和评论
#     user_stories = Story.objects.filter(author=user).order_by('-created_at')
#     user_comments = Comment.objects.filter(author=user).order_by('-created_at')
#
#     context = {
#         'user': user,
#         'user_stories': user_stories,
#         'user_comments': user_comments,
#     }
#     return render(request, 'profile.html', context)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def update_profile(request):
    """更新用户资料"""
    try:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX 请求
            data = json.loads(request.body)
            user = request.user

            # 更新用户信息
            if 'email' in data:
                user.email = data['email']
            if 'phone' in data:
                user.phone = data['phone']
            if 'pen_name' in data:
                user.pen_name = data['pen_name']
            if 'bio' in data:
                user.bio = data['bio']
            if 'notify_comments' in data:
                user.notify_comments = data['notify_comments']
            if 'notify_likes' in data:
                user.notify_likes = data['notify_likes']

            user.save()

            return JsonResponse({
                'success': True,
                'message': '资料更新成功！'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '无效的请求'
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'更新失败：{str(e)}'
        })



# views.py - 修改 upload_avatar 函数
@login_required
@csrf_exempt
def upload_avatar(request):
    """上传用户头像"""
    try:
        if request.method == 'POST' and 'avatar' in request.FILES:
            avatar_file = request.FILES['avatar']

            print(f"🔄 开始头像上传流程...")

            # 文件验证
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if avatar_file.content_type not in allowed_types:
                return JsonResponse({
                    'success': False,
                    'message': '只支持JPEG、PNG、GIF、WEBP格式的图片'
                })

            if avatar_file.size > 2 * 1024 * 1024:
                return JsonResponse({
                    'success': False,
                    'message': '图片大小不能超过2MB'
                })

            # 生成文件路径并上传
            file_path = oss_client.generate_file_path(request.user.id, avatar_file.name)
            uploaded_path = oss_client.upload_file(avatar_file, file_path)

            if uploaded_path:
                # 更新用户头像字段（存储文件路径）
                request.user.head = uploaded_path
                request.user.save()
                print(f"✅ 用户头像字段已更新: {uploaded_path}")

                # 生成公共URL返回给前端
                avatar_url = oss_client.get_file_url(uploaded_path)

                # 确保返回完整的URL
                if not avatar_url.startswith(('http://', 'https://')):
                    # 如果是相对路径，添加完整域名
                    from django.contrib.sites.shortcuts import get_current_site
                    current_site = get_current_site(request)
                    avatar_url = f"http://{current_site.domain}{avatar_url}"

                print(f"✅ 头像公共URL: {avatar_url}")

                return JsonResponse({
                    'success': True,
                    'message': '头像上传成功',
                    'avatar_url': avatar_url
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': '头像上传失败，请检查权限'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': '请选择头像文件'
            })
    except Exception as e:
        print(f"❌ 头像上传异常: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'上传失败: {str(e)}'
        })



from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Count
from user.models import CustomerUser
from stories.models import Story, Category
import json


# 检查管理员权限
def check_admin_permission(request):
    if request.user.is_authenticated and request.user.is_staff:
        return JsonResponse({'is_admin': True})
    return JsonResponse({'is_admin': False})


# 控制台统计数据
@login_required
def dashboard_stats(request):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': '权限不足'})

    try:
        total_users = CustomerUser.objects.count()
        total_stories = Story.objects.count()
        total_categories = Category.objects.count()

        return JsonResponse({
            'success': True,
            'total_users': total_users,
            'total_stories': total_stories,
            'total_categories': total_categories
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# 用户管理
@login_required
@require_http_methods(["GET", "PUT", "DELETE"])
@csrf_exempt
def admin_users(request, user_id=None):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': '权限不足'})

    if request.method == 'GET':
        try:
            # 修复：使用正确的模型字段，添加角色和状态信息
            users = CustomerUser.objects.annotate(story_count=Count('story')).values(
                'id', 'username', 'email', 'date_joined', 'is_staff', 'is_active', 'story_count'
            )

            user_list = []
            for user in users:
                user_list.append({
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'is_staff': user['is_staff'],
                    'is_active': user['is_active'],
                    'role': 'admin' if user['is_staff'] else 'user',
                    'created_at': user['date_joined'].strftime('%Y-%m-%d %H:%M'),
                    'story_count': user['story_count']
                })

            return JsonResponse({'success': True, 'users': user_list})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    elif request.method == 'PUT':
        try:
            if user_id == request.user.id:
                return JsonResponse({'success': False, 'error': '不能修改自己的账户'})

            user = CustomerUser.objects.get(id=user_id)
            data = json.loads(request.body)

            # 更新用户信息
            if 'email' in data:
                user.email = data['email']
            if 'is_staff' in data:
                user.is_staff = data['is_staff']
            if 'is_active' in data:
                user.is_active = data['is_active']
            if 'role' in data:
                user.is_staff = (data['role'] == 'admin')

            user.save()

            return JsonResponse({'success': True, 'message': '用户信息更新成功'})
        except CustomerUser.DoesNotExist:
            return JsonResponse({'success': False, 'error': '用户不存在'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    elif request.method == 'DELETE':
        try:
            if user_id == request.user.id:
                return JsonResponse({'success': False, 'error': '不能删除自己的账户'})

            user = CustomerUser.objects.get(id=user_id)

            # 检查是否为管理员，管理员不能被删除
            if user.is_staff:
                return JsonResponse({'success': False, 'error': '不能删除管理员用户'})

            user.delete()
            return JsonResponse({'success': True})
        except CustomerUser.DoesNotExist:
            return JsonResponse({'success': False, 'error': '用户不存在'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


# 故事管理
@login_required
@require_http_methods(["GET", "DELETE", "PATCH"])  # 新增PATCH方法处理审核
def admin_stories(request, story_id=None):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': '权限不足'})

    if request.method == 'GET':
        try:
            # 获取前端传递的状态筛选参数（默认显示待审核）
            status_filter = request.GET.get('status', 'pending')
            query = Story.objects.select_related('author', 'category').all()

            # 根据状态筛选
            if status_filter in ['pending', 'approved', 'rejected']:
                query = query.filter(status=status_filter)

            stories = query.order_by('-created_at')

            story_list = []
            for story in stories:
                story_list.append({
                    'id': story.id,
                    'title': story.title,
                    'content': story.content,
                    'author': story.author.username,
                    'category_name': story.category.name if story.category else '未分类',
                    'created_at': story.created_at.strftime('%Y-%m-%d %H:%M'),
                    'status': story.status,  # 返回审核状态
                    'status_text': dict(Story.STATUS_CHOICES)[story.status],  # 状态中文描述
                    'review_note': story.review_note  # 审核备注
                })

            return JsonResponse({'success': True, 'stories': story_list})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    # 新增：处理审核操作（通过/拒绝）
    elif request.method == 'PATCH':
        try:
            data = json.loads(request.body)
            # 审核结果（approved/rejected）和备注
            status = data.get('status')
            review_note = data.get('review_note', '')

            if status not in ['approved', 'rejected']:
                return JsonResponse({'success': False, 'error': '无效的审核状态'})

            story = Story.objects.get(id=story_id)
            story.status = status
            story.review_note = review_note  # 保存审核备注（尤其是拒绝原因）
            story.save()

            return JsonResponse({'success': True})
        except Story.DoesNotExist:
            return JsonResponse({'success': False, 'error': '故事不存在'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    # 保持删除功能不变
    elif request.method == 'DELETE':
        try:
            story = Story.objects.get(id=story_id)
            story.delete()
            return JsonResponse({'success': True})
        except Story.DoesNotExist:
            return JsonResponse({'success': False, 'error': '故事不存在'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

# 分类管理
@login_required
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
@csrf_exempt
def admin_categories(request, category_id=None):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': '权限不足'})

    if request.method == 'GET':
        try:
            categories = Category.objects.annotate(story_count=Count('story')).values(
                'id', 'name', 'description', 'story_count','created_at'
            )

            category_list = []
            for category in categories:
                category_list.append({
                    'id': category['id'],
                    'name': category['name'],
                    'description': category['description'],
                    'story_count': category['story_count'],
                    'created_at': category['created_at'].isoformat()  # 格式化日期为ISO格式
                })

            return JsonResponse({'success': True, 'categories': category_list})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            description = data.get('description', '').strip()

            if not name:
                return JsonResponse({'success': False, 'error': '分类名称不能为空'})

            if Category.objects.filter(name=name).exists():
                return JsonResponse({'success': False, 'error': '分类名称已存在'})

            category = Category.objects.create(
                name=name,
                description=description
            )

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            description = data.get('description', '').strip()

            if not name:
                return JsonResponse({'success': False, 'error': '分类名称不能为空'})

            category = Category.objects.get(id=category_id)

            # 检查名称是否与其他分类重复
            if Category.objects.filter(name=name).exclude(id=category_id).exists():
                return JsonResponse({'success': False, 'error': '分类名称已存在'})

            category.name = name
            category.description = description
            category.save()

            return JsonResponse({'success': True})
        except Category.DoesNotExist:
            return JsonResponse({'success': False, 'error': '分类不存在'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    elif request.method == 'DELETE':
        try:
            category = Category.objects.get(id=category_id)
            category.delete()
            return JsonResponse({'success': True})
        except Category.DoesNotExist:
            return JsonResponse({'success': False, 'error': '分类不存在'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


from django.contrib.auth.decorators import login_required, user_passes_test

def admin_required(view_func):
    """管理员权限装饰器"""
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/user/login/')
        if not request.user.is_staff:
            # 非管理员用户重定向到首页，而不是登录页面
            return redirect('/stories/index/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# 使用装饰器简化视图函数
@login_required
@admin_required
def admin_dashboard(request):
    return render(request, 'admin_console.html')

@login_required
@admin_required
def admin_users_page(request):
    return render(request, 'admin_user.html')

@login_required
@admin_required
def admin_stories_page(request):
    return render(request, 'admin_review.html')

@login_required
@admin_required
def admin_categories_page(request):
    return render(request, 'admin_class.html')


# 专用的 API 视图
@require_http_methods(["GET"])
def api_user_profile(request):
    """获取当前用户信息的专用 API"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': '请先登录'})

    user = request.user
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'phone': user.phone,
        'pen_name': user.pen_name,
        'bio': user.bio,
        'avatar_url': user.get_avatar_url(),
        'role': user.role,
        'created_at': user.created_at.isoformat(),
        'notify_comments': user.notify_comments,
        'notify_likes': user.notify_likes
    }

    return JsonResponse({
        'success': True,
        'user': user_data
    })


@require_http_methods(["GET"])
def api_user_stories(request):
    """获取用户故事的专用 API"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': '请先登录'})

    user_stories = Story.objects.filter(author=request.user).order_by('-created_at')

    stories_data = []
    for story in user_stories:
        stories_data.append({
            'id': story.id,
            'title': story.title,
            'content': story.content[:200] + '...' if len(story.content) > 200 else story.content,
            'category': story.category.name if story.category else '未分类',
            'status': story.status,
            'likes': story.likes,
            'created_at': story.created_at.isoformat(),
            'img_id': story.img_id
        })

    return JsonResponse({
        'success': True,
        'stories': stories_data,
        'count': len(stories_data)
    })



