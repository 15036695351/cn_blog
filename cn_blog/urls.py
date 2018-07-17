"""cn_blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path,re_path

from blog import views
urlpatterns = [
    path('updown/', views.updown),
    path('admin/', admin.site.urls),
    path('login/', views.login, name='login'),
    path('index/', views.index, name='index'),
    path('code/', views.code),
    path('logout/', views.logout, name='logout'),
    path('comment/', views.comment),
    path('backstage/', views.backstage,name="backstage"),    # 个人站点后台管理页面

    path('backstage/add/', views.add, name='add'),
    path('upload/', views.upload),
    path('backstage/delete/', views.delete,name='delete'),
    re_path('backstage/editor/(?P<article_id>\d+)', views.editor,name='editor'),


    # 文章详情页
    re_path("(?P<username>\w+)/article_detail/(?P<user_id>\d+)$",views.article_detail),
    re_path('(?P<username>\w+)/$', views.homesite),

    re_path('(?P<username>\w+)/articles/(?P<article_id>\d+)$', views.article_detail),

    re_path('(?P<username>\w+)/(?P<condition>category|tag|achrive)/(?P<params>.*)', views.homesite),




]
