#!/usr/bin/env python
# *_ coding:utf-8 _*_
import json
import time
from datetime import datetime
import re
import requests
from SaveDataBase import UpdateData
import getheaders


class GetInfo(object):
    def __init__(self, stocklist):
        self.list = stocklist

    # 对所选股票进行同时处理

    def getinfo(self):
        yesterday = 0
        # 获取雪球首页session
        headers = {
            'Host': 'xueqiu.com',
            'User-Agent': getheaders.get_user_agent()
        }
        # 访问雪球官网，获取COOKIE
        session = requests.session()
        while True:
            try:
                headers['User-Agent'] = getheaders.get_user_agent()
                session.get(url='https://xueqiu.com/', headers=headers)
                break
            except:
                continue
        while True:

            # 新增，判断当天日期是否为today，如果不是，today时间变化为当天日期，并且获取雪球cookie，如果是则pass
            today = time.strftime("%Y-%m-%d", time.localtime())
            if today == yesterday:
                pass
            else:
                yesterday = today
                while True:
                    try:
                        headers['User-Agent'] = getheaders.get_user_agent()
                        session.get(url='https://xueqiu.com/', headers=headers)
                        break
                    except:
                        continue

            timenow = str(time.strftime("%H:%M:%S", time.localtime()))
            # 当此时时间大于停盘时间pass 否则抓取数据
            if ((timenow > '12:15:00') & (timenow < '13:00:00')) | (timenow > '19:20:00') or (timenow < '09:25:00'):
                time.sleep(60)
                pass
            else:
                urllen = len(self.list)

                # 创建一个list[]将处理后的数组传入，再一次性存入数据库
                datalist1 = list()
                datalist2 = list()

                # 创建一个此时的数据长度标志出来，方便之后在选取网站的循环中拿到定时间段的数据
                while True:
                    try:
                        headers['User-Agent'] = getheaders.get_user_agent()
                        headers['Host'] = r'stock.xueqiu.com'
                        r = session.get(
                            'https://stock.xueqiu.com/v5/stock/chart/minute.json?symbol=00001&period=1d',
                            headers=headers)
                        res = r.content
                        break
                    except:
                        time.sleep(0.1)
                        continue
                pattern = re.compile(r'\[(?:\[??[^\[]*?\])')
                standard = pattern.findall(str(res))
                standardlen = len(json.loads(standard[0]))

                for i in range(urllen):

                    # 传入数据库？
                    stock_code = self.list[i][0]
                    stock_uni_code = self.list[i][2]
                    abc_code = self.list[i][1]
                    print(stock_code)

                    url = 'https://stock.xueqiu.com/v5/stock/chart/minute.json?symbol=' + str(stock_code) + '&period=1d'
                    newheaders = {
                        'Host': 'stock.xueqiu.com',
                        'User-Agent': getheaders.get_user_agent()
                    }
                    # 防止拿不到请求的代码1
                    while True:
                        try:
                            newheaders['User-Agent'] = getheaders.get_user_agent()
                            r1 = session.get(url, headers=newheaders)
                            r = r1.content
                            break
                        except:
                            time.sleep(0.1)
                            continue

                    result = pattern.findall(str(r))
                    if len(json.loads(result[0])) == 0:
                        pass
                    else:
                        length = len(json.loads(result[0]))

                        # 判断情况，爬取数据
                        # 先判断是否停盘
                        if ((timenow > '12:05:00') & (timenow < '13:00:00')) | (timenow > '16:15:00'):
                            # 停盘时获取最新的数据，方法getinfo1
                            info = json.loads(result[0])[-1]
                            # 尝试对重复的方法进行封装
                            result1 = self.getinfo1(info, stock_uni_code, abc_code)
                            datalist1.append(result1)
                        elif length > 2:
                            p1info = json.loads(result[0])[standardlen - 2]
                            p2info = json.loads(result[0])[standardlen - 3]
                            result1 = self.getinfo1(p1info, stock_uni_code, abc_code)
                            result2 = self.getinfo1(p2info, stock_uni_code, abc_code)
                            #   初始化存入时间的列表，方便在爬取过程中进行比较
                            datalist1.append(result1)
                            datalist2.append(result2)
                    time.sleep(0.2)
                print("跑完110")

                # 将获得的数据打包存入list后，传入GetAllDataBase(),然后再一次性存入数据库
                # 所用股票信息存在datalist中
                update1 = UpdateData(datalist1)
                update1.update()
                update2 = UpdateData(datalist2)
                update2.update()

    def getinfo1(self, info, sec_uni_code, stock_code):
        #     将当前爬取的时间放入列表
        nowtime = self.gettime(info)
        price = self.getprice(info)
        volume = self.getvolume(info)
        amount = self.getamount(info)
        # 可以修改输入数组长度
        avg_price = self.getavgprice(info)
        differ = self.getupdownp(info)
        differ_range = self.getpricelimit(info)

        return sec_uni_code, str(stock_code), nowtime, price, avg_price, differ, differ_range, volume, amount

    def getprice(self, info):
        """
        用于获取价格
        :param info:
        :return:
        """

        return float(info['current']) if info['current'] else 0
        # 获取成交额

    def getamount(self, info):
        return float(info['amount']) if info['current'] else 0

        # 用于获取当前时间

    def gettime(self, info):
        timestamp = info['timestamp']
        local_str_time = datetime.fromtimestamp(timestamp / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        return local_str_time

        # 用于获取成交量

    def getvolume(self, info):
        return float(info['volume']) if info['volume'] else 0

        # 获取当前均价

    def getavgprice(self, info):
        return float(info['avg_price']) if info['avg_price'] else 0

        # 用于获得涨跌值

    def getupdownp(self, info):
        return float(info['chg']) if info['chg'] else 0

        # 用于计算涨跌幅

    def getpricelimit(self, info):
        return float(info['percent']) if info['percent'] else 0

    # def modify_null(self, value):
    #     """
    #
    #     :param value:
    #     :return:
    #     """
    #
    #     return  float(value) if value else 0
    #
    # precent = self.modify_null(info['percent'])
