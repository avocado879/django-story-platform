import random
import string
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomerUser(AbstractUser):
    # 角色选择
    ROLE_CHOICES = (
        ('admin', '管理员'),
        ('user', '普通用户'),
    )

    phone = models.CharField(max_length=11, verbose_name="手机号", null=True)
    head = models.ImageField(upload_to="user/", null=True, blank=True, default='img/mao.jpg')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user', verbose_name="角色")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # 如果是超级用户，自动设置为管理员角色
        if self.is_superuser:
            self.role = 'admin'
        super().save(*args, **kwargs)

    def get_role_display(self):
        """获取角色显示名称"""
        return dict(self.ROLE_CHOICES).get(self.role, self.role)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class PasswordResetCode(models.Model):
    email = models.EmailField(verbose_name="邮箱")
    code = models.CharField(max_length=6, verbose_name="验证码")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    is_used = models.BooleanField(default=False, verbose_name="是否已使用")

    class Meta:
        verbose_name = "密码重置验证码"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def is_expired(self):
        """检查验证码是否过期（5分钟内有效）"""
        return timezone.now() > self.created_at + timedelta(minutes=5)

    @classmethod
    def generate_code(cls, email):
        """生成验证码并保存"""
        # 生成6位随机数字验证码
        code = ''.join(random.choices(string.digits, k=6))

        # 保存验证码到数据库
        return cls.objects.create(email=email, code=code)