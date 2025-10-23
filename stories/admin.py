from .models import Category, Story,CommentLike,Comment,Like,Save
from django.contrib import admin

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    pass

@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    pass

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    pass

@admin.register(Save)
class SaveAdmin(admin.ModelAdmin):
    pass
