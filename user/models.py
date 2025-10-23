import random
import string
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomerUser(AbstractUser):
    # 角色选择
    ROLE_CHOICES = (
        ('admin', '管理员'),
        ('user', '普通用户'),
    )

    # 添加缺失的 role 字段
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name="角色"
    )

    phone = models.CharField(max_length=11, verbose_name="手机号", null=True)
    # 修改头像字段为URL字段
    head = models.CharField(
        max_length=500,
        verbose_name="头像URL",
        null=True,
        blank=True,
        default=settings.DEFAULT_AVATAR_URL
    )

    def get_avatar_url(self):
        """获取头像完整URL"""
        if self.head:
            # 获取头像的文件路径或URL字符串
            avatar_value = str(self.head)  # 转换为字符串

            # 如果已经是完整URL，直接返回
            if avatar_value.startswith(('http://', 'https://')):
                return avatar_value

            # 如果是文件路径，直接拼接OSS基础URL
            try:
                # 直接返回OSS的基础URL + 文件路径
                return f"http://storyai2.oss-cn-hangzhou.aliyuncs.com/{avatar_value.lstrip('/')}"
            except Exception as e:
                print(f"获取头像URL失败: {e}")
                # 返回默认头像的OSS直接链接
                return "http://storyai2.oss-cn-hangzhou.aliyuncs.com/static/img/book.jpg"
        else:
            # 返回默认头像的OSS直接链接
            return "http://storyai2.oss-cn-hangzhou.aliyuncs.com/static/img/book.jpg"



    # phone = models.CharField(max_length=11, verbose_name="手机号", null=True)
    # head = models.ImageField(upload_to="user/", null=True, blank=True, default='img/mao.jpg')
    # role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user', verbose_name="角色")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # 添加个人资料相关字段
    pen_name = models.CharField(max_length=100, blank=True, verbose_name="笔名")
    bio = models.TextField(max_length=500, blank=True, verbose_name="个人简介")
    notify_comments = models.BooleanField(default=True, verbose_name="评论通知")
    notify_likes = models.BooleanField(default=True, verbose_name="点赞通知")

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