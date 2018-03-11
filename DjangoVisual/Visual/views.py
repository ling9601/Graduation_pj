from django.shortcuts import render
from my_main.models import ScrapyItem,UserItem_dj,post_Item_dj
from django.views.decorators.csrf import csrf_exempt
from Visual.ass.matplot_visual import create_pic
from scrapyd_api import ScrapydAPI
from Visual.ass.data import location_count
import json
from Visual.ass.crawl import crawl_weibo,check_user_exist
from django.views.generic import ListView
from Visual.ass.my_wordcloud import create_wordcloud

# Create your views here.
scrapyd = ScrapydAPI('http://localhost:6800')
@csrf_exempt
def search_user(request):
    id = request.POST.get('id', None)  # take url comes from client. (From an input may be?)
    ## 检测id合理性
    if not id:
        return render(request, 'Visual/dashboard.html', context={'tips': '请输入id', 'pics': False})

    if not id.isdigit():
        return render(request, 'Visual/dashboard.html', context={'tips': '请输入id', 'pics': False})

    ## 检测该用户是否存在
    if check_user_exist(id):
        result=ScrapyItem.objects.filter(id=id) #查询是否已经执行过该id的爬虫
        if result:
            status = scrapyd.job_status('default', result[0].task_id)
            if status=='running':  #未查询到任务，则返回空字符串
                return render(request,'Visual/dashboard.html',context={'tips':'爬取数据中，请等待','pics':False})
            else:
                creation=create_pic(id)
                creation.gender()
                creation.fans_num()
                creation.post_freq()
                creation.get_pic()
                creation.fans_authen()

                user=UserItem_dj.objects.get(id=id)
                if user.gender=='m':
                    dgender='男'
                else:
                    dgender='女'
                if user.verified_type == -1:
                    verified_type = '普通'
                elif user.verified_type == 200:
                    verified_type = '初级达人'
                elif user.verified_type == 220:
                    verified_type = '高级达人'
                elif user.verified_type == 0:
                    verified_type = '黄V'
                else:
                    verified_type='蓝V'
                user_info_dict={'user_name':user.screen_name, 'description':user.description,
                                'location':user.location,'follow_count':user.follow_count,
                                'followers_count':user.followers_count,'gender':dgender,
                                'statuses_count':user.statuses_count,'verified_type':verified_type}
                return render(request, 'Visual/dashboard.html', context={'tips': '用户id: {}'.format(id), 'pics': True,'user_info_dict':user_info_dict,'option_js':json.dumps(location_count(id))})
        else:
            task = scrapyd.schedule('default', 'fans', id=id)
            item=ScrapyItem(id=id,task_id=task)
            item.save()
            return render(request,'Visual/dashboard.html',context={'tips':'开始爬取数据，请等待'})
    else:
        return render(request, 'Visual/dashboard.html', context={'tips': '该id不存在'})

def index(request):
    return render(request,'Visual/dashboard.html',context={'tips':'请输入用户id','pics':False})

class UserView(ListView):
    model = UserItem_dj
    template_name = 'Visual/listing.html'
    context_object_name = 'user_list'
    paginate_by = 5

def show(request,id):

    creation = create_pic(id)
    creation.gender()
    creation.fans_num()
    creation.post_freq()
    creation.get_pic()
    creation.fans_authen()

    user = UserItem_dj.objects.get(id=id)
    if user.gender == 'm':
        dgender = '男'
    else:
        dgender = '女'
    if user.verified_type == -1:
        verified_type = '普通'
    elif user.verified_type == 200:
        verified_type = '初级达人'
    elif user.verified_type == 220:
        verified_type = '高级达人'
    elif user.verified_type == 0:
        verified_type = '黄V'
    else:
        verified_type = '蓝V'
    user_info_dict = {'user_name': user.screen_name, 'description': user.description,
                      'location': user.location, 'follow_count': user.follow_count,
                      'followers_count': user.followers_count, 'gender': dgender,
                      'statuses_count': user.statuses_count, 'verified_type': verified_type}
    return render(request, 'Visual/dashboard.html',
                  context={'tips': '用户id: {}'.format(id), 'pics': True, 'user_info_dict': user_info_dict,
                           'option_js': json.dumps(location_count(id))})
@csrf_exempt
def search_weibo(request):
    id = request.POST.get('id', None)
    if not id:
        return render(request, 'Visual/weibo.html', context={'tips': '请输入微博id'})
    if not id.isdigit():
        return render(request, 'Visual/weibo.html', context={'tips': '请输入微博id，数字'})

    post_dict=crawl_weibo(id)
    if post_dict==0:    #微博不存在
        return render(request,'Visual/weibo.html',context={'tips':'微博id不存在'})
    else:
        post=post_Item_dj(**post_dict)
        create_wordcloud(post.text)
        text_len=len(post.text)
        return render(request, 'Visual/weibo.html',
                      context={'tips': '微博id: {}    微博长度: {}'.format(id,text_len), 'post': post})
def weibo(request):
    return render(request, 'Visual/weibo.html',context={'tips':'请输入微博id'})