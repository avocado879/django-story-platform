from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json

from .models import Story, Category, Comment, Like, Save, CommentLike

from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json

from .models import Story, Category, Comment, Like, Save, CommentLike
from .utils import APIResponseMixin

# 创建混入类实例
api_mixin = APIResponseMixin()


def index(request):
    context = {'message': '欢迎来到故事平台'}

    # 如果是 API 请求，返回 JSON
    if request.GET.get('format') == 'json' or request.headers.get('Accept') == 'application/json':
        return api_mixin.render_to_api_response(context)

    return render(request, 'index.html', context)


def stories(request):
    # 只显示审核通过的故事
    stories_list = Story.objects.filter(status='approved').order_by('-created_at')
    categories = Category.objects.all()

    # 分类筛选
    selected_category = request.GET.get('category', 'all')
    if selected_category != 'all':
        stories_list = stories_list.filter(category__name=selected_category)

    # 排序
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'popular':
        stories_list = stories_list.order_by('-likes', '-created_at')

    context = {
        'stories': stories_list,
        'categories': categories,
        'selected_category': selected_category,
        'sort_by': sort_by,
    }

    # 如果是 API 请求，返回 JSON
    if request.GET.get('format') == 'json' or request.headers.get('Accept') == 'application/json':
        return api_mixin.render_to_api_response(context)

    return render(request, 'stories.html', context)


def story_detail(request, story_id):
    try:
        story = Story.objects.get(id=story_id)
        comments = Comment.objects.filter(story=story, parent=None).select_related('author')

        # 检查用户是否点赞和收藏故事
        user_liked = False
        user_saved = False
        if request.user.is_authenticated:
            user_liked = Like.objects.filter(user=request.user, story=story).exists()
            user_saved = Save.objects.filter(user=request.user, story=story).exists()

            # 检查用户是否点赞过每个评论
            for comment in comments:
                comment.user_liked = CommentLike.objects.filter(
                    user=request.user,
                    comment=comment
                ).exists()

                # 检查回复评论的点赞状态
                for reply in comment.replies.all():
                    reply.user_liked = CommentLike.objects.filter(
                        user=request.user,
                        comment=reply
                    ).exists()

        context = {
            'story': story,
            'comments': comments,
            'user_liked': user_liked,
            'user_saved': user_saved,
        }

        # 如果是 API 请求，返回 JSON
        if request.GET.get('format') == 'json' or request.headers.get('Accept') == 'application/json':
            return api_mixin.render_to_api_response(context)

        return render(request, 'story_detail.html', context)
    except Story.DoesNotExist:
        error_context = {'error': '故事不存在'}
        if request.GET.get('format') == 'json' or request.headers.get('Accept') == 'application/json':
            return JsonResponse(error_context, status=404)
        return render(request, '404.html', status=404)


@login_required
@require_POST
@csrf_exempt
def save_story(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': '请先登录'})

        title = request.POST.get('title')
        content = request.POST.get('content')
        category_name = request.POST.get('category')
        img_id = request.POST.get('img_id')
        read_time = request.POST.get('read_time')

        print(f"保存故事数据: {title}, {category_name}")

        # 根据分类名称获取或创建分类对象
        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults={'description': f'{category_name}类故事'}
        )

        # 创建故事对象，明确设置状态为待审核
        story = Story(
            title=title,
            content=content,
            category=category,
            img_id=img_id,
            read_time=read_time,
            author=request.user,
            status='pending'  # 明确设置为待审核状态
        )
        story.save()

        print(f"故事保存成功，ID: {story.id}, 状态: {story.status}")

        return JsonResponse({
            'success': True,
            'message': '故事已提交审核，请等待管理员审核通过后发布到故事库'
        })

    except Exception as e:
        print(f"保存故事错误: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

def generate_story(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title')
        style = request.POST.get('style')
        category_id = request.POST.get('category')
        content = request.POST.get('content')

        try:
            category = Category.objects.get(id=category_id)
            story = Story(
                title=title,
                style=style,
                category=category,
                content=content,
                author=request.user
            )
            story.save()

            messages.success(request, '故事发布成功！')
            return redirect('stories:stories')

        except Category.DoesNotExist:
            messages.error(request, '所选分类不存在')
        except Exception as e:
            messages.error(request, f'发布失败：{str(e)}')

    return render(request, 'generate.html', {
        'categories': categories
    })





@login_required
@require_POST
def toggle_like(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    like, created = Like.objects.get_or_create(user=request.user, story=story)

    if not created:
        like.delete()
        story.likes -= 1
        liked = False
    else:
        story.likes += 1
        liked = True

    story.save()

    return JsonResponse({
        'success': True,
        'liked': liked,
        'likes_count': story.likes
    })


@login_required
@require_POST
def toggle_save(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    save, created = Save.objects.get_or_create(user=request.user, story=story)

    if not created:
        save.delete()
        saved = False
    else:
        saved = True

    return JsonResponse({
        'success': True,
        'saved': saved
    })


@login_required
@require_POST
def add_comment(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    data = json.loads(request.body)
    content = data.get('content', '').strip()
    parent_id = data.get('parent_id')

    if not content:
        return JsonResponse({'success': False, 'message': '评论内容不能为空'})

    parent = None
    if parent_id:
        parent = get_object_or_404(Comment, id=parent_id)

    comment = Comment.objects.create(
        story=story,
        author=request.user,
        parent=parent,
        content=content
    )

    return JsonResponse({
        'success': True,
        'comment': {
            'id': comment.id,
            'author': comment.author.username,
            'author_avatar': comment.author.get_avatar_url(),
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
            'is_author': True,
            'parent_id': parent.id if parent else None
        }
    })


@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    comment.delete()

    return JsonResponse({'success': True})


@login_required
@require_POST
def delete_story(request, story_id):
    story = get_object_or_404(Story, id=story_id, author=request.user)
    story.delete()

    return JsonResponse({'success': True})


@require_GET
def get_story_likes(request, story_id):
    """获取故事的实时点赞数"""
    try:
        story = Story.objects.get(id=story_id)
        return JsonResponse({
            'success': True,
            'likes_count': story.likes
        })
    except Story.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '故事不存在'
        })


@require_POST
def get_multiple_story_likes(request):
    """批量获取多个故事的点赞数"""
    try:
        data = json.loads(request.body)
        story_ids = data.get('story_ids', [])

        # 将字符串ID转换为整数
        story_ids = [int(id) for id in story_ids if id.isdigit()]

        stories = Story.objects.filter(id__in=story_ids).values('id', 'likes')
        likes_data = [
            {
                'story_id': str(story['id']),
                'likes_count': story['likes']
            }
            for story in stories
        ]

        return JsonResponse({
            'success': True,
            'likes_data': likes_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@login_required
@require_POST
def toggle_comment_like(request, comment_id):
    """切换评论点赞状态"""
    try:
        comment = get_object_or_404(Comment, id=comment_id)

        # 检查用户是否已经点赞过这个评论
        comment_like, created = CommentLike.objects.get_or_create(
            user=request.user,
            comment=comment
        )

        if not created:
            # 如果已经点赞过，取消点赞
            comment_like.delete()
            comment.likes = max(0, comment.likes - 1)
            liked = False
        else:
            # 如果没有点赞过，添加点赞
            comment.likes += 1
            liked = True

        comment.save()

        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': comment.likes
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@require_GET
def search_stories(request):
    """搜索故事"""
    query = request.GET.get('q', '').strip()

    if not query:
        return JsonResponse({
            'success': False,
            'message': '请输入搜索关键词'
        })

    try:
        # 搜索标题或分类包含关键词的故事
        stories = Story.objects.filter(
            models.Q(title__icontains=query) |
            models.Q(category__name__icontains=query)
        ).select_related('category').order_by('-created_at')

        # 构建响应数据
        stories_data = []
        for story in stories:
            stories_data.append({
                'id': story.id,
                'title': story.title,
                'category': story.category.name,
                'excerpt': story.content[:100] + '...' if len(story.content) > 100 else story.content,
                'likes': story.likes,
                'read_time': story.read_time,
                'created_at': story.created_at.strftime('%Y-%m-%d'),
                'img_id': story.img_id or 100,
                'author': story.author.username
            })

        return JsonResponse({
            'success': True,
            'stories': stories_data,
            'count': len(stories_data),
            'query': query
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'搜索失败: {str(e)}'
        })