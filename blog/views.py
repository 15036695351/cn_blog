from django.shortcuts import render

# Create your views here.

from django.shortcuts import render,redirect,reverse,HttpResponse
from django.contrib import auth
from django.db.models import Avg,Count,Min,Max

from blog.models import UserInfo,Blog,Category,Tag,Comment,Article2Tag,Article,ArticleUpDown

from utils.code import check_code
import random
from io import BytesIO


def code(request):
    """
    生成图片验证码
    :param request:
    :return:
    """
    img, random_code = check_code()
    request.session['random_code'] = random_code
    from io import BytesIO
    stream = BytesIO()
    img.save(stream, 'png')
    return HttpResponse(stream.getvalue())


def login(request):
    if request.method == "GET":
        return render(request, "login.html")
    user = request.POST.get("user")
    pwd = request.POST.get("pwd")
    code = request.POST.get("code")
    print("code",code)
    if code.upper() != request.session['random_code'].upper():
        return render(request, 'login.html', {"msg": "验证码输入错误"})

    user = auth.authenticate(username=user,password=pwd)
    if user:
        auth.login(request,user)
        return redirect("/index/")
    return render(request,"login.html",{'msg': '用户名或密码错误'})


def logout(request):
    auth.logout(request)
    return redirect(reverse("index"))

def index(request):
    # if request.method == "POST":
    article_list = Article.objects.all()
    return render(request,"index.html",locals())

def homesite(request,username,**kwargs):
    user = UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, "not_found.html")
    blog = user.blog

    # 查询当前用户发布的所有文章
    if not kwargs:
        article_list = Article.objects.filter(user__username=username)
    else:
        condition = kwargs.get("condition")

        params = kwargs.get("params")

        if condition == "category":
            article_list = Article.objects.filter(user__username=username).filter(category__title=params)
        elif condition == "tag":
            article_list = Article.objects.filter(user__username=username).filter(tags__title=params)
        else:
            year,month = params.split("/")
            article_list = Article.objects.filter(user__username=username).filter(create_time__year=year,create_time__month=month)


    # # 查询当前站点每一个分类的名称以及对应的文章数
    #
    # cate_list = Category.objects.filter(blog=blog).values('pk').annotate(c=Count("article__title")).values_list("title","c")
    #
    #
    # # 查询当前站点每一个标签的名称以及对应的文章数
    # tag_list = Tag.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")).values_list("title","c")
    #
    # # 日期归档==>需要制定日期格式
    # date_list = Article.objects.filter(user=user).extra(select={"y_m_date":"strftime('%%Y/%%m',create_time)"}).\
    #     values("y_m_date").annotate(c=Count("title")).values_list("y_m_date","c")

    if not article_list:
        return render(request,"not_found.html")

    return render(request,"homesite.html",locals())

def article_detail(request,username,article_id):

    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog

    article_obj=Article.objects.filter(pk=article_id).first()

    # 将对这篇文章的所有评论筛选出来
    comment_list = Comment.objects.filter(article_id=article_id)
    return render(request,'article_detail.html',locals())


import json
from django.db.models import F,Q
from django.http import JsonResponse

from django.db import transaction
def updown(request):
    if request.method == "POST":
        user_id = request.user.pk   # 全局变量，可以通过request请求直接获取
        article_id = request.POST.get("article_id")
        is_up = json.loads(request.POST.get("is_up"))
        # 判断is_up是点赞操作还有踩灭操作 ，直接取is_up会变成字符串，而我们需要True或Flase

        response = {"state":True, "msg":None}   # 响应的数据内容

        # 过滤ArticleUpDown表里的内容
        article_obj=ArticleUpDown.objects.filter(user_id=user_id,article_id=article_id).first()
        if article_obj:  # 已经操作过----》点赞过或踩灭过
            response["state"] = False
            response["handled"] = article_obj.is_up    # 根据is_up来判别是什么操作
        else:   # 没有操作过
            with transaction.atomic(): # 给 ArticleUpDown表增加数据和Article表更新数据绑定事务：都成功或都失败
                ArticleUpDown.objects.create(is_up=is_up, article_id=article_id, user_id=user_id)
                if is_up:   # 判断是点赞还是踩灭，之后给相应的字段值 +1
                    Article.objects.filter(pk=article_id).update(up_count=F("up_count")+1)
                else:
                    Article.objects.filter(pk=article_id).update(down_count=F("down_count")+1)
        return JsonResponse(response)

    else:
        return HttpResponse("请先登录")

def comment(request):
    if request.method == "POST":
        user_id = request.user.pk
        article_id = request.POST.get("article_id")
        content = request.POST.get("content")
        parent_id = request.POST.get("parent_id")

        # 哪位用户在什么时间对什么文章进行了什么评论内容，有无父评论
        with transaction.atomic():
            comment = Comment.objects.create(user_id=user_id,article_id=article_id,content=content,parent_comment_id=parent_id)
            Article.objects.filter(pk=article_id).update(comment_count=F("comment_count")+1)

        response = {"state":True}
        response["timer"]=comment.create_time.strftime("%Y-%m-%d %X")
        response["content"] = content
        response["user"] = request.user.username

        return JsonResponse(response)


def backstage(request):
    user = request.user # 登录之后可以从cookies与session中获取用户相关信息
    article_list = Article.objects.filter(user=user)
    return render(request,"backstage/backstage.html",locals())




def add(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        user = request.user
        cate_pk = request.POST.get("cate")
        tags_pk_list = request.POST.getlist("tags")

        # 对发表文章的内容进行过滤
        from bs4 import BeautifulSoup
        soup= BeautifulSoup(content,"html.parser")
        for tag in soup.find_all():
            if tag.name in ["script",]:
                tag.decompose()

        # 文章描述desc：先对文章进行纯文本过滤，之后对文章进行切片
        desc = soup.text[0:150]
        article_obj = Article.objects.create(title=title, content=str(soup),user=user,category_id=cate_pk,desc=desc)

        for tag_pk in tags_pk_list:    # 标签有很多个,需要循环添加
            Article2Tag.objects.create(article_id=article_obj.pk,tag_id=tag_pk)

        return redirect(reverse("backstage"))
    else:
        blog = request.user.blog
        cate_list = Category.objects.filter(blog=blog)
        tags = Tag.objects.filter(blog=blog)
        return render(request,"backstage/add.html",locals())



import os
from cn_blog import settings
def upload(request):
    # print(request.FILES)

    obj = request.FILES.get("upload_img")   # 获取上传文件的文件
    file_name = obj.name

    path = os.path.join(settings.BASE_DIR,"static","upload",file_name)
    with open(path,"wb")as f:   # 以写的形式打开文件
        for line in obj:
            f.write(line)

    import json
    res ={
        "error":0,
        "url":"/static/upload/"+file_name
    }
    return HttpResponse(json.dumps(res))



def editor(request,article_id):
    article = Article.objects.filter(pk=article_id).first()
    blog = request.user.blog  # user ==》blog==》Category
    cate_list = Category.objects.filter(blog=blog)
    if request.method == 'POST':
        title = request.POST.get("title")
        desc = request.POST.get("desc")
        content = request.POST.get('content')
        category_id = request.POST.get('cate_id')

        Article.objects.filter(pk=article_id).update(
            title=title,
            desc=desc,
            content=content,
            category_id=category_id,
        )
        return redirect(reverse("backstage"))

    return render(request,"backstage/editor.html",locals())







def delete(request):
    if request.method == "POST":
        delete_id = request.POST.get("delete_id")
        # print("delete_id",delete_id,"############")
        Article.objects.filter(pk=delete_id).delete()
        return HttpResponse(json.dumps({"status":1}))

























































