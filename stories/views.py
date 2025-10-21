from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from stories.models import Category, Story
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
# Create your views here.
def index(request):
    return render(request, 'index.html')


@login_required
@require_POST
@csrf_exempt
def save_story(request):
    try:
        # 检查用户是否登录
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': '请先登录'})

        title = request.POST.get('title')
        content = request.POST.get('content')
        category = request.POST.get('category')
        img_id = request.POST.get('img_id')
        read_time = request.POST.get('read_time')

        print(f"保存故事数据: {title}, {category}")  # 调试信息

        # 创建故事对象
        story = Story(
            title=title,
            content=content,
            category=category,
            img_id=img_id,
            read_time=read_time,
            user=request.user  # 关联当前用户
        )
        story.save()

        print(f"故事保存成功，ID: {story.id}")  # 调试信息

        return JsonResponse({'success': True})

    except Exception as e:
        print(f"保存故事错误: {str(e)}")  # 调试信息
        return JsonResponse({'success': False, 'error': str(e)})

def generate_story(request):
    # 获取所有分类用于下拉选择
    categories = Category.objects.all()

    if request.method == 'POST':
        # 从表单中获取数据
        title = request.POST.get('title')
        style = request.POST.get('style')
        category_id = request.POST.get('category')
        content = request.POST.get('content')

        try:
            # 获取对应的分类对象
            category = Category.objects.get(id=category_id)

            # 创建并保存故事
            story = Story(
                title=title,
                style=style,
                category=category,
                content=content
            )
            story.save()

            # 显示成功消息并跳转到故事列表或详情页
            messages.success(request, '故事发布成功！')
            return redirect('stories:story_list')  # 假设你有故事列表页的URL名称

        except Category.DoesNotExist:
            messages.error(request, '所选分类不存在')
        except Exception as e:
            messages.error(request, f'发布失败：{str(e)}')

    # GET请求时显示表单页面
    return render(request, 'generate.html', {
        'categories': categories
    })

def stories(request):
    # 获取所有分类
    categories = Category.objects.all()

    # 获取所有故事
    stories = Story.objects.all()

    # 处理分类筛选
    category_filter = request.GET.get('category', 'all')
    if category_filter != 'all':
        stories = stories.filter(category__name=category_filter)

    # 处理排序
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'popular':
        stories = stories.order_by('-likes')
    else:  # 默认按最新排序
        stories = stories.order_by('-created_at')

    context = {
        'stories': stories,
        'categories': categories,
        'selected_category': category_filter,
        'sort_by': sort_by,
    }

    return render(request, 'stories.html', context)


def story_detail(request, story_id):
    try:
        story = Story.objects.get(id=story_id)
        context = {
            'story': story,
        }
        return render(request, 'story_detail.html', context)
    except Story.DoesNotExist:
        # 处理故事不存在的情况
        return render(request, '404.html', status=404)