#!/usr/bin/env python
# *_ coding:utf-8 _*_


import logging
import pymysql
import redis


class UpdateData(object):
    def __init__(self, datalist):
        self.datalist = datalist

    def update(self):
        # 链接数据库
        if len(self.datalist) == 0:
            pass
        else:
            length = len(self.datalist)
            mapping = {}
            for i in range(length):
                sec_uni_code = self.datalist[i][0]
                stock_code = self.datalist[i][1]
                trade_date = self.datalist[i][2]
                open = self.datalist[i][3]
                avg_price = self.datalist[i][4]
                differ = self.datalist[i][5]
                differ_range = self.datalist[i][6]
                volume = self.datalist[i][7]
                amount = self.datalist[i][8]
                name = 'price_hk_time_' + str(stock_code)
                key = str(trade_date)+"_"+str(stock_code)
                value = str(sec_uni_code)+','+str(stock_code)+','+str(trade_date)+','+str(open)+','+str(avg_price)+','+str(differ)+','+str(differ_range)+','+str(volume)+','+str(amount)+','
                mapping[key] = value
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.hmset(name=self.datalist[0][2], mapping=mapping)
