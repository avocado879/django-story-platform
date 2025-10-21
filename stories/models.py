from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from DjangoProject4 import settings
from user.models import CustomerUser


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Story(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=50)
    img_id = models.IntegerField(default=1)
    read_time = models.IntegerField(default=1)
    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
# class Story(models.Model):
#     title = models.CharField(max_length=200)
#     content = models.TextField()
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(default=timezone.now)
#     img_id = models.IntegerField(default=1)
#     likes = models.IntegerField(default=0)
#     read_time = models.IntegerField(default=3)
#     is_default = models.BooleanField(default=False)
#
#     class Meta:
#         ordering = ['-created_at']
#
#     def __str__(self):
#         return self.title


class StoryLike(models.Model):
    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'story')


class StorySave(models.Model):
    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'story')


class Comment(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    author = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']


class UserProfile(models.Model):
    user = models.OneToOneField(CustomerUser, on_delete=models.CASCADE)
    pen_name = models.CharField(max_length=100, blank=True)
    default_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    notify_comments = models.BooleanField(default=True)
    notify_likes = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username