# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo as pymongo
import logging
import datetime
import re
from .items import UserItem,fans_2_Item,fans_1_Item,post_Item,comment_Item
from scrapy.exceptions import DropItem
from my_main.models import UserItem_dj,fans_1_Item_dj,fans_2_Item_dj,post_Item_dj,comments_Item_dj



def clean_time(time,null_to_str=False):
    today = datetime.datetime.now().date()
    if '小时' in time:  # x分钟前；x小时前
        hours=int(re.search('(\d+)',time).group(1))
        if hours>datetime.datetime.now().hour:  #昨天
            time = str(today-datetime.timedelta(days=1))
        else:
            time=str(today)
    elif '分钟' in time:
        minutes=int(re.search('(\d+)',time).group(1))
        if datetime.datetime.now().hour==0 and minutes>datetime.datetime.now().minute:   #昨天
            time=str(today-datetime.timedelta(days=1))
        else:
            time=str(today)
    elif '昨' in time:  # 昨天 xx
        yesterday = today - datetime.timedelta(days=1)
        time = str(yesterday)
    elif len(time) == 5:  # xx-xx  (02-01) 2月1号
        this_year = str(today)[:5] + time
        time = this_year
    elif len(time)!=10:
        if null_to_str:
            return 'null'
        else:
            return None
    return time

def clean_dict(my_dict, attr_list):  #数据整理，清洗
    my_dict_clean={}
    for attr in attr_list:
        if attr=='created_at':                 #统一化时间显示
            my_dict_clean[attr]=clean_time(my_dict[attr])
            my_dict_clean['created_at_org']=my_dict[attr]
        elif attr=='pics':
            my_dict_clean['pics']=('pics' in my_dict)
        elif attr=='author_id':
            my_dict_clean['author_id']=my_dict['user']['id']
        elif attr=='retweeted_status':          #转发微博的信息
            if 'retweeted_status'in my_dict:
                my_dict_clean[attr]=True
                my_dict_clean['retweeted_text']=my_dict[attr]['text']
            else:
                my_dict_clean[attr] = False
        else:
            my_dict_clean[attr] = my_dict[attr]

    return my_dict_clean

def fans_2_to_dict(my_dict,attr_list,master_id):
    my_dict_clean={}
    my_dict_clean['master_id']=master_id
    for attr in attr_list:
        if attr=='sid':
            my_dict_clean['sid'] = my_dict['id']
        else:
            my_dict_clean[attr] = my_dict[attr]
    return my_dict_clean



class WeiboScrapyApiPipeline(object):
    def __init__(self):
        #数据库操作
        self.CONN=pymongo.MongoClient('localhost',27017)
        self.DBNAME='syn_12'
        self.user_col=self.CONN[self.DBNAME]['user']
        self.fans_1_col=self.CONN[self.DBNAME]['fans_1']
        self.fans_2_col=self.CONN[self.DBNAME]['fans_2']
        self.post_col=self.CONN[self.DBNAME]['post']
        self.comments_col=self.CONN[self.DBNAME]['comments']
        self.user_col.create_index([('id', pymongo.ASCENDING)], unique=True)
        self.fans_1_col.create_index([('sid', pymongo.ASCENDING),('master_id',pymongo.ASCENDING)], unique=True)
        self.fans_2_col.create_index([('sid', pymongo.ASCENDING),('master_id',pymongo.ASCENDING)], unique=True)
        self.post_col.create_index([('id', pymongo.ASCENDING)], unique=True)
        self.comments_col.create_index([('id', pymongo.ASCENDING)], unique=True)
        #debug变量
        self.count_user=0
        self.count_fans_1=0
        self.count_fans_2=0
        #用于去重的list
        # self.fans_2_buf=[]
        self.post_buf=[]
    def process_item(self, item, spider):
        if isinstance(item,UserItem):               # User
            self.count_user+=1
            try:
                UserItem_dj(**item).save()
            except Exception as e:
                logging.warning(('dj_1',str(e)))
            try:
                self.user_col.insert_one(dict(item))
            except Exception as e:
                logging.debug(('Exception_1',str(e)))
        elif isinstance(item,fans_1_Item):              #fans_1
            self.count_fans_1+=1
            try:
                fans_1_Item_dj(**item).save()
            except Exception as e:
                logging.warning(('dj_2',str(e)))
            try:
                self.fans_1_col.insert_one(dict(item))
            except Exception as e:
                logging.debug(('Exception_2',str(e)))
        elif isinstance(item,fans_2_Item):              #fans_2
            page=item['page']
            master_id=item['master_id']
            item_list=[]
            card_list = []
            attr_list=['sid','follow_count','followers_count','statuses_count','verified_type','description','screen_name','mbrank','mbtype']
            for card in page:
                if card['card_type']==10:
                    user=card['user']
                    fans_2_dict=fans_2_to_dict(user,attr_list,master_id)
                    card_list.append(fans_2_dict)
                    item_list.append(fans_2_Item_dj(**fans_2_dict))
            ### fans_2写入django影响爬虫速度，故放弃写入django
            # fans_2中经常会遇到重复写入
            # try:
            #     fans_2_Item_dj.objects.bulk_create(item_list)
            # except Exception as e:
            #     logging.warning(('fans_2_error',str(e)))
            #     for i in item_list: #遇到重复，则回滚，逐一插入
            #         try:
            #             i.save()
            #         except Exception as e:
            #             logging.warning(('fans_2_error_sub',str(e)))
            try:
                result = self.fans_2_col.insert_many(card_list, ordered=False)
            except pymongo.errors.BulkWriteError as e:
                logging.debug(('BulkWriteError: ', str(e)))
        elif isinstance(item,post_Item):                   #post
            attr_list = ['author_id', 'attitudes_count', 'comments_count', 'created_at', 'id', 'pics', 'reposts_count',
                         'source', 'text', 'retweeted_status']
            page = item['page']
            card_list = []
            item_list=[]
            for card in page:
                if card['card_type'] == 9:
                    my_dict=clean_dict(card['mblog'], attr_list)
                    card_list.append(my_dict)
                                                            # dj
                    item_list.append(post_Item_dj(**my_dict))

            self.post_buf+=item_list    #用buf来缓存所有的数据
            try:
                result = self.post_col.insert_many(card_list, ordered=False)
            except pymongo.errors.BulkWriteError as e:
                logging.debug(('BulkWriteError: ', str(e)))
        elif isinstance(item,comment_Item):
            page=item['page']
            comments_list=[]
            item_list=[]
            for i in page:
                comment_dict={'created_at':clean_time(i['created_at'],null_to_str=True),
                                      'id':i['id'],
                                      'like_counts':i['like_counts'],
                                      'source':i['source'],
                                      'text':i['text'],
                                      'user_id':i['user']['id'],
                                      'screen_name':i['user']['screen_name'],
                                      'post_id':int(item['post_id'])}
                comments_list.append(comment_dict)
                item_list.append(comments_Item_dj(**comment_dict))
            try:    #mongodb 插入
                result=self.comments_col.insert_many(comments_list,ordered=False)
            except pymongo.errors.BulkWriteError as e:
                logging.debug(('BulkWriteError: ', str(e)))
            try:    #dj 插入
                comments_Item_dj.objects.bulk_create(item_list)
            except Exception as e:
                logging.warning(('comments_error',str(e)))
                for i in item_list: #遇到重复，则回滚，逐一插入
                    try:
                        i.save()
                    except Exception as e:
                        logging.warning(('comments_error_sub',str(e)))
        return DropItem()

    def close_spider(self,spider):
        # logging.debug(('count_user',self.count_user))
        # logging.debug(('count_fans_1',self.count_fans_1))
        # logging.debug(('count_fans_2',self.count_fans_2))
        # fans_2_clean_list=[]      #去重
        # fans_2_id_set=set()
        # for i in self.fans_2_buf:
        #     if not i.id in fans_2_id_set:
        #         fans_2_clean_list.append(i)
        #         fans_2_id_set.add(i.id)
        # try:
        #     fans_2_Item_dj.objects.bulk_create(fans_2_clean_list)
        # except Exception as e:
        #     logging.warning(('post_error',str(e)))

        post_clean_list=[]      #去重
        post_id_set=set()
        for i in self.post_buf:
            if not i.id in post_id_set:
                post_clean_list.append(i)
                post_id_set.add(i.id)
        try:
            post_Item_dj.objects.bulk_create(post_clean_list)
        except Exception as e:
            logging.warning(('post_error',str(e)))
