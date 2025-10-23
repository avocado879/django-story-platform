from django.db import models
from django.conf import settings
from django.utils import timezone

from user.models import CustomerUser


class Category(models.Model):
    """故事分类"""
    name = models.CharField(max_length=100, verbose_name="分类名称")
    description = models.TextField(blank=True, verbose_name="分类描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "故事分类"
        verbose_name_plural = verbose_name
        ordering = ['name']

    def __str__(self):
        return self.name


class Story(models.Model):
    """故事模型"""
    # 新增审核状态选项
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '已发布'),
        ('rejected', '已拒绝'),
    )

    title = models.CharField(max_length=200, verbose_name="故事标题")
    content = models.TextField(verbose_name="故事内容")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="故事分类")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="作者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    likes = models.IntegerField(default=0, verbose_name="点赞数")
    views = models.IntegerField(default=0, verbose_name="阅读数")
    img_id = models.CharField(max_length=100, blank=True, verbose_name="图片ID")
    read_time = models.IntegerField(default=0, verbose_name="阅读时长")

    # 新增审核状态字段，默认为"待审核"
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="审核状态"
    )
    # 可选：添加审核备注（管理员拒绝时填写原因）
    review_note = models.TextField(blank=True, null=True, verbose_name="审核备注")

    class Meta:
        verbose_name = "故事"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def increment_views(self):
        """增加阅读数"""
        self.views += 1
        self.save(update_fields=['views'])


class CommentLike(models.Model):
    """评论点赞模型"""
    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, verbose_name='用户')
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, verbose_name='评论')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        unique_together = ('user', 'comment')  # 确保用户不能重复点赞同一评论
        verbose_name = '评论点赞'
        verbose_name_plural = '评论点赞'

class Comment(models.Model):
    story = models.ForeignKey('Story', on_delete=models.CASCADE, verbose_name='故事')
    author = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, verbose_name='作者')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                              verbose_name='父评论', related_name='replies')
    content = models.TextField(verbose_name='评论内容')
    likes = models.IntegerField(default=0, verbose_name='点赞数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author.username}: {self.content[:20]}'

    @property
    def like_count(self):
        """获取评论点赞数"""
        return self.likes


class Like(models.Model):
    """点赞模型"""
    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, verbose_name="用户")
    story = models.ForeignKey(Story, on_delete=models.CASCADE, verbose_name="故事")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="点赞时间")

    class Meta:
        verbose_name = "点赞"
        verbose_name_plural = verbose_name
        unique_together = ('user', 'story')  # 确保用户对同一故事只能点赞一次
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} 点赞了 {self.story.title}'


class Save(models.Model):
    """收藏模型"""
    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, verbose_name="用户")
    story = models.ForeignKey(Story, on_delete=models.CASCADE, verbose_name="故事")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="收藏时间")

    class Meta:
        verbose_name = "收藏"
        verbose_name_plural = verbose_name
        unique_together = ('user', 'story')  # 确保用户对同一故事只能收藏一次
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} 收藏了 {self.story.title}'




class StoryView(models.Model):
    """故事浏览记录"""
    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, null=True, blank=True,
                             verbose_name="用户")
    story = models.ForeignKey(Story, on_delete=models.CASCADE, verbose_name="故事")
    ip_address = models.GenericIPAddressField(verbose_name="IP地址")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="浏览时间")

    class Meta:
        verbose_name = "浏览记录"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        username = self.user.username if self.user else '匿名用户'
        return f'{username} 浏览了 {self.story.title}'

# from django.db import models
#
# # Create your models here.
# from django.db import models
# from django.contrib.auth.models import User
# from django.utils import timezone
#
# from DjangoProject4 import settings
# from user.models import CustomerUser
#
#
# class Category(models.Model):
#     name = models.CharField(max_length=50, unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.name
#
#
# class Story(models.Model):
#     title = models.CharField(max_length=200)
#     content = models.TextField()
#     category = models.CharField(max_length=50)
#     img_id = models.IntegerField(default=1)
#     read_time = models.IntegerField(default=1)
#     user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
# # class Story(models.Model):
# #     title = models.CharField(max_length=200)
# #     content = models.TextField()
# #     category = models.ForeignKey(Category, on_delete=models.CASCADE)
# #     created_at = models.DateTimeField(default=timezone.now)
# #     img_id = models.IntegerField(default=1)
# #     likes = models.IntegerField(default=0)
# #     read_time = models.IntegerField(default=3)
# #     is_default = models.BooleanField(default=False)
# #
# #     class Meta:
# #         ordering = ['-created_at']
# #
# #     def __str__(self):
# #         return self.title
#
#
# class StoryLike(models.Model):
#     user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
#     story = models.ForeignKey(Story, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         unique_together = ('user', 'story')
#
#
# class StorySave(models.Model):
#     user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
#     story = models.ForeignKey(Story, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         unique_together = ('user', 'story')
#
#
# class Comment(models.Model):
#     story = models.ForeignKey(Story, on_delete=models.CASCADE)
#     author = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
#     content = models.TextField()
#     created_at = models.DateTimeField(default=timezone.now)
#
#     class Meta:
#         ordering = ['-created_at']
#
#