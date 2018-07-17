from django import template

from  blog.models import UserInfo,Category,Tag,Article
from django.db.models import Avg,Count,Min,Max




register = template.Library()


@register.inclusion_tag("base_core.html")
def get_query_data(username):
    user = UserInfo.objects.filter(username=username).first()

    blog = user.blog
    # 查询当前站点每一个分类的名称以及对应的文章数

    cate_list = Category.objects.filter(blog=blog).values('pk').annotate(c=Count("article__title")).values_list("title",
                                                                                                                "c")

    # 查询当前站点每一个标签的名称以及对应的文章数
    tag_list = Tag.objects.filter(blog=blog).annotate(c=Count("article__title")).values_list("title", "c")

    # 日期归档==>需要制定日期格式
    date_list = Article.objects.filter(user=user).extra(select={"y_m_date": "strftime('%%Y/%%m',create_time)"}). \
        values("y_m_date").annotate(c=Count("title")).values_list("y_m_date", "c")


    return {"blog": blog, "username": username, "cate_list": cate_list, "tag_list": tag_list, "date_list": date_list}