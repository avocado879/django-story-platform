from django.contrib import admin
from django.urls import path, include

from .views import logins, register, logout, forgot_password, send_verify_code, reset_password, profile_view, update_profile,upload_avatar
from . import views

app_name = 'user'
urlpatterns = [
    # 原有的 URL 保持不变
    path('login/',logins,name='login'),
    path('register/',register,name='register'),
    path('logout/',logout,name='logout'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('send_verify_code/', send_verify_code, name='send_verify_code'),
    path('reset_password/', reset_password, name='reset_password'),
    path('profile/', profile_view, name='profile'),
    path('update_profile/', update_profile, name='update_profile'),

    # 新增用户 API 路由
    path('api/profile/', views.api_user_profile, name='api_user_profile'),
    path('api/stories/', views.api_user_stories, name='api_user_stories'),

    # 管理页面路由（保持不变）
    path('', views.admin_dashboard, name='admin_index'),
    path('check_permission/', views.check_admin_permission, name='check_permission'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_users_page/', views.admin_users_page, name='admin_users_page'),
    path('admin_stories_page/', views.admin_stories_page, name='admin_stories_page'),
    path('admin_categories_page/', views.admin_categories_page, name='admin_categories_page'),

    # API路由 - 使用不同的路径
    path('api/admin_users/', views.admin_users, name='admin_users_api'),
    path('api/admin_users/<int:user_id>/', views.admin_users, name='admin_user_detail_api'),
    path('api/admin_stories/', views.admin_stories, name='admin_stories_api'),
    path('api/admin_stories/<int:story_id>/', views.admin_stories, name='admin_story_detail_api'),
    path('api/admin_categories/', views.admin_categories, name='admin_categories_api'),
    path('api/admin_categories/<int:category_id>/', views.admin_categories, name='admin_category_detail_api'),

    # 新增头像上传URL
    path('upload_avatar/', upload_avatar, name='upload_avatar'),
]