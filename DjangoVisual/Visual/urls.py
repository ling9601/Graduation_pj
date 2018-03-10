from django.conf.urls import url

from Visual import views

app_name='Visual'
urlpatterns=[
    url(r'^$',views.index,name='index'),
    url(r'^weibo/$',views.weibo,name='weibo'),
    url(r'^search_user/$',views.search_user,name='search_user'),
    url(r'^listing/$',views.UserView.as_view(),name='listing'),
    url(r'^show/(?P<id>[0-9]+)/$',views.show,name='show'),
    url(r'^search_weibo/$',views.search_weibo,name='search_weibo')
]