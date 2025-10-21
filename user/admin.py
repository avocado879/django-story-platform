from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomerUser, PasswordResetCode


@admin.register(CustomerUser)
class CustomerUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'get_role_display', 'is_staff', 'is_active', 'created_at')
    list_filter = ('role', 'is_staff', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'phone')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('个人信息'), {'fields': ('email', 'phone', 'head', 'role')}),
        (_('权限'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('重要日期'), {'fields': ('last_login', 'date_joined', 'created_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_staff', 'is_active'),
        }),
    )

    readonly_fields = ('created_at',)

    def get_role_display(self, obj):
        return obj.get_role_display()

    get_role_display.short_description = '角色'

    def get_queryset(self, request):
        # 管理员可以看到所有用户，普通员工只能看到普通用户
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(role='user')


@admin.register(PasswordResetCode)
class PasswordResetCodeAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'created_at', 'is_used', 'is_expired')
    list_filter = ('is_used', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('created_at',)

    def is_expired(self, obj):
        return obj.is_expired()

    is_expired.boolean = True
    is_expired.short_description = '是否过期'