"""
URL configuration for story_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.urls import path
from . import views
app_name = 'stories'
urlpatterns = [
    path('index/', views.index, name='index'),
    # path('login/', views.login_view, name='login'),
    # path('register/', views.register_view, name='register'),
    # path('logout/', views.logout_view, name='logout'),
    path('generate/', views.generate_story, name='generate_story'),
    path('stories/', views.stories, name='stories'),
    path('save_story/', views.save_story, name='save_story'),
    # path('story/<int:story_id>/', views.story_detail, name='story_detail'),
    # path('story/<int:story_id>/like/', views.toggle_like, name='toggle_like'),
    # path('story/<int:story_id>/save/', views.toggle_save, name='toggle_save'),
    # path('story/<int:story_id>/comment/', views.add_comment, name='add_comment'),
    # path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    # path('story/<int:story_id>/delete/', views.delete_story, name='delete_story'),
    # path('story/save/', views.save_story, name='save_story'),
    # path('profile/update/', views.update_profile, name='update_profile'),
]