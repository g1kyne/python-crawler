import requests  # 请求库
from urllib.parse import urlencode  # 解析链接
from lxml import etree  # 解析页面
from requests import RequestException

import langconv
import re  # 正则表达式，用于匹配去除评论中的符号


def get_top_page(start):
    """
    获取电影排行页面的html
    :param start:从第几页开始
    :return:请求正常时返回第start页的html
    """
    params = {  # 参数
        'start': start,
        'filter': '',
    }
    # top250的网址为：https://movie.douban.com/top250?start=0&filter=  第二页start=25(每页25部电影)
    # urlencode()，可以把key-value这样的键值对转换成我们想要的格式，返回的是a=1&b=2这样的字符串
    url = 'https://movie.douban.com/top250?' + urlencode(params)
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }
        # 发送请求
        response = requests.get(url,headers=headers)
        # 若请求成功，返回该页面的html
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('get_top_page() Error')
        return None


# 测试
# top_page = get_top_page(0)
# print(top_page)
# 至此得到了第1页的html页面内容


def get_comment_link(top_page):
    """
    获取每页每部电影的评论链接前部分
    :param top_page: 每页电影的html内容
    :return:每页电影的评论链接前部分内容
    """
    html = etree.HTML(top_page)  # 初始化，得到html页面
    # 得到电影的链接 https://movie.douban.com/subject/1851857/
    # 完整地址为https://movie.douban.com/subject/1851857/comments?start=20(每页评论+20)&limit=20&sort=new_score&status=P
    res = html.xpath('//div[@class="hd"]//a/@href')
    return res


# 测试
# comment_link = get_comment_link(top_page)
# print(comment_link)
# 至此获取到了第1页每部电影的评论链接的前部分


def get_comment_page(comment_link, start):
    """
    根据get_comment_link（）得到的部分评论链接，得到评论页面的html
    :param comment_link: 部分评论链接
    :param start: 评论开始的页面，每页+20
    :return:
    """
    # 完整地址为https://movie.douban.com/subject/1851857/comments?start=20(每页评论+20)&limit=20&sort=new_score&status=P
    params = {  # 参数列表
        'start': start,
        'limit': '20',
        'sort': 'new_score',
        'status': 'P'
    }
    # 完整的评论地址
    url = comment_link + 'comments?' + urlencode(params)
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return 'Error'
    except RequestException:
        print('get_comment_page() Error')
        return None


# 测试 这里返回的是None，请求错误？？？？
# comment_page = get_comment_page(str(comment_link), str(0))
# print(comment_page)
# 至此获取到了评论页面的html


def get_comment(comment_page):
    """
    根据评论页面获取评论
    :param comment_page: 评论页面的html
    :return:返回值为评论内容
    """
    html = etree.HTML(comment_page)
    res = html.xpath('//div[@class="comment"]/p/span/text()')
    return res
# 至此得到了评论内容

def Traditional2Simplified(sentence):
    """
    将sentence中的繁体字转为简体字
    :param sentence:
    :return:返回转化后的简体
    """
    sentence = langconv.Converter('zh-hans').convert(sentence)
    return sentence


def clear(string):
    """
    清理评论数据
    :param string:
    :return:
    """
    string = string.strip()  # 去掉空格等空白符号
    # re.sub(pattern,repl,string,[count],[flags]
    # pattern:正则中的模式字符串  repl：替换的字符串  string：要被处理的字符串
    string = re.sub('[A-Za-z0-9]', '', string)  # 去掉英文字母，数字
    string = re.sub(r"[！!？｡。，&;＂★＃＄％＆＇（）＊＋－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃「」『』【】"
                    r"〔〕〖〗〘〙#〚〛〜〝〞/?=~〟,〰–—‘’‛“”„‟…‧﹏.]", " ", string)  # 去掉中文符号
    string = re.sub(r"[!\'\"#。$%&()*+,-.←→/:~;<=>?@[\\]^_`_{|}~", " ", string)  # 去掉英文符号
    return Traditional2Simplified(string).lower()  # 所有的英文都换成小写


def save_to_txt(results):
    """
    存为txt文件
    :param results:
    :return:
    """
    for result in results:
        result = clear(result)
        with open('top250电影影评.txt','a',encoding='utf-8') as f:
            f.write(result)
            f.write('\n----------------------------------------------------\n')


print('开始了哦')
for start in range(0, 250, 25):  # 从第1页开始，步长为25，一共爬10页
    print('正在爬第' + str(int(start/25+1)) + '页的电影')
    top_page = get_top_page(start)
    comment_link = get_comment_link(top_page)
    for i in range(25):  # 一页有25个电影
        print('正在爬第' + str(i+1) + '个电影')
        for j in range(0, 200, 20):  # 一个电影一页有20个评论 从第一页开始，步长为20，一共爬10页
            print('正在爬第' + str(int(j/20+1)) + '页的评论')
            comment_page = get_comment_page(comment_link[i], j)  # 爬取第i个电影  start=j页的评论
            comment = get_comment(comment_page)
            save_to_txt(comment)
        print('第' + str(i+1) + '个电影爬完了')











