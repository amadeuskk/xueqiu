#!/usr/bin/env python
# *_ coding:utf-8 _*_


import logging
import pymysql
from GetInfo import GetInfo
import multiprocessing

import sys

# 传参
neednum = 0


def run(num):
    # 先从数据库中拿取2000多支股票信息，然后再将其存入list
    # 链接数据库
    while True:
        try:
            db = pymysql.connect(host='10.11.255.110', port=31306, user='rreportor', password='saWQR432QR',
                                 db='r_reportor',
                                 charset='utf8')
            cursor = db.cursor()
            break
        except:
            continue
    sql = "SELECT sec_code,abc_code,sec_uni_code FROM sec_basic_info WHERE sec_type=1004017 AND end_date IS NULL;"
    cursor.execute(sql)
    stock_info = cursor.fetchall()
    if cursor:
        cursor.close()
    db.close()
    # 此时的urllist就是所有没有停牌股票网站
    # 先从urllist中拿取40条网站信息放在ulist中
    ulist = []
    num = int(num)
    try:
        for fill_list in range(num, num + 110):
            ulist.append(stock_info[fill_list])
    except:
        pass
    getinfo = GetInfo(ulist)
    getinfo.getinfo()

def main():
    num = int(neednum)
    # 此时最多爬取的股票支数为2310，如股票支数超过，则多开进程即可（每只进程跑110支股票）
    for i in range(11):
        p = multiprocessing.Process(target=run, args=(num,))
        p.start()
        num += 110


if __name__ == '__main__':
    log_path = 'spider_ovsec_hk_price_{0}.log'.format(neednum)
    logging.basicConfig(filename=log_path, format='%(asctime)s %(name)s %(levelname)s [line %(lineno)s]: %(message)s',
                        filemode='w', level=logging.INFO)
    main()