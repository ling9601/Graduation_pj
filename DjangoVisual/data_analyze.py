import pymongo as pymongo
import re
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


def is_chinese(uchar):
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False


def ana_description(data_list):
    aa = 0
    ab = 0
    ba = 0
    bb = 0
    for i in data_list:

        if i['zombie']:
            if i['description']:
                aa += 1
            else:
                ab += 1
        else:
            if i['description']:
                ba += 1
            else:
                bb += 1
    print(aa)
    print(ab)
    print(ba)
    print(bb)

def ana_fo_foer(data_list):
    zombie_list=[]
    normal_list=[]
    folloers_couont_ave=0
    follow_count_ave=0
    for i in data_list:
        folloers_couont_ave+=i['followers_count']
        follow_count_ave+=i['follow_count']
    folloers_couont_ave/=len(data_list)
    follow_count_ave/=len(data_list)
    print('follower: {}'.format(folloers_couont_ave))
    print('follow: {}'.format(follow_count_ave))

    count_zombie=0
    count_normal=0

    for i in data_list:
        if i['zombie']==1 and i['followers_count']<2*folloers_couont_ave and i['follow_count']<4*follow_count_ave:
            zombie_list.append(i)
            count_zombie+=1
        elif i['zombie']==0 and i['followers_count']<2*folloers_couont_ave and i['follow_count']<4*follow_count_ave:
            normal_list.append(i)
            count_normal+=1

    plt.plot([i['follow_count'] for i in zombie_list],[i['followers_count'] for i in zombie_list],'ko',label='zombie')
    plt.plot([i['follow_count'] for i in normal_list],[i['followers_count'] for i in normal_list],'b.',label='normal')
    plt.xlabel('关注数')
    plt.ylabel('粉丝数')
    print('zombie: {}'.format(count_zombie))
    print('normal: {}'.format(count_normal))
    plt.legend()
    plt.show()


def ana_ratio(data_list):
    zombie_list=[]
    normal_list=[]
    for i in data_list:
        if i['follow_count']==0:
            i['follow_count']=1
        i['ratio']=i['followers_count']/i['follow_count']


        if i['ratio']>10:
            i['ratio']=10
        if i['zombie']:
            zombie_list.append(i)
        else:
            normal_list.append(i)
    plt.plot([i['ratio'] for i in zombie_list],'ko',label='zombie')
    plt.plot([i['ratio'] for i in normal_list],'b.',label='normal')
    plt.legend()
    plt.show()
    plt.close()

def ana_description(data_list):
    zombie_list=[]
    normal_list=[]
    for i in data_list:
        if i['zombie']:
            zombie_list.append(i)
        else:
            normal_list.append(i)
    count_zombie=0
    count_normal=0
    for i,ii in zip(zombie_list,normal_list):
        if i['description']:
            count_zombie+=1
        if ii['description']:
            count_normal+=1
    print('zombie_description_ratio: {}'.format(count_zombie/len(zombie_list)))
    print('normal_description_ratio: {}'.format(count_normal/len(normal_list)))


def ana_name_has_num(data_list):
    zombie_had_count=0
    normal_had_count=0
    for i in data_list:
        if i['zombie'] and re.search(r'\d',i['screen_name']):
            zombie_had_count+=1
        elif not i['zombie'] and re.search(r'\d',i['screen_name']):
            normal_had_count+=1
    print(zombie_had_count)
    print(normal_had_count)

def ana_mode_1(data_list):
    count_zombie=0
    count_normal=0
    count_id=0
    for i in data_list:
        name=i['screen_name']
        print(name)
        if is_chinese(name[0]) and name[-1].isdigit() and str(i['sid']) not in name and i['zombie']:
            count_zombie+=1
        elif is_chinese(name[0]) and name[-1].isdigit() and str(i['sid']) not in name and not i['zombie']:
            count_normal+=1
        elif str(i['sid']) in name:
            count_id+=1
    print(count_zombie)
    print(count_normal)
    print(count_id)


def main():
    CONN = pymongo.MongoClient('localhost', 27017)
    col = CONN['new_label']['fans']

    data_list = list(col.find())

    zombie_count=0
    normal_count=0
    for i in data_list:
        if i['zombie']:
            zombie_count+=1
        else:
            normal_count+=1
    print('zombie: {}'.format(zombie_count))
    print('normal: {}'.format(normal_count))

    # ana_fo_foer(data_list)

    # ana_ratio(data_list)

    # ana_description(data_list)

    # ana_name_has_num(data_list)

    ana_mode_1(data_list)

if __name__ == '__main__':
    main()
