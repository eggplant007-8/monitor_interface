# -*- coding: utf-8 -*-
'''
Created on 2013-8-5

@author: jiangleiqian
'''
import sys
import json
import curses
import urllib2
import optparse
import locale
import math
import time
import thread

locale.setlocale(locale.LC_ALL,"")

message = 'function.py [(int)START] [(int)END] [(int)SORT] \n \
      START > 0 \n \
      SORT in [1, 2, 3]'

parser = optparse.OptionParser(usage=message)
(opts, args) = parser.parse_args()

START = int(sys.argv[1])
END = int(sys.argv[2])
SORT = int(sys.argv[3])


def url_report(screen):
    keys = ["实例id", "ip", "已建数据库", "实际建数据库", "数据库资源数误差", "磁盘大小", "磁盘使用量", "磁盘数用率"]
    value_len = []
    for key in keys:
        value_len.append(int(round(len(key) * 0.8)))
#        value_len.append(len(key))
    while True:
        screen.clear()
        url = "http://192.168.194.129:8087/?action=desc_instance_used&begin=%s&end=%s&sort=%s" % (1, 10, 1)
#        url = "http://10.168.0.105:8087/?action=desc_instance_used&begin=%s&end=%s&sort=%s" % (START, END, SORT)
        papi = urllib2.urlopen(url, timeout=10).read()
        papi = json.loads(papi)
        keys = [" 实例id ", " ip ", " 已建数据库 ", " 实际建数据库 ", " 数据库资源数误差 ", " 磁盘大小 ", " 磁盘使用量 ", " 磁盘数用率 "]
        values = ["id", "ip", "quota_db_num", "actually_use_db", "db_differ_num", "capacity_total", "capacity_used", "ratio_used"]
        page_len, line_len = screen.getmaxyx()#获取屏幕显示尺寸
        line = 1

        for instance in papi:
            index = 0
            while index < len(keys):
                if len(str(instance[values[index]])) > value_len[index]:
                    value_len[index] = len(str(instance[values[index]])) + 2
                index += 1
        multiple = int(math.ceil(sum(value_len[0:len(keys)]) / float(line_len)))
#        index = 0
        screen.addstr(line, 1, time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        line += 1
        if line + 3 * multiple > page_len:
            time.sleep(1)
            continue

        for index, item in enumerate(keys):
            integer, remainder = divmod(sum(value_len[0:index]), line_len)
            screen.addstr(line + integer, remainder, "+" + '-' * value_len[index])
            screen.addstr(line + 1 * multiple + integer, remainder, "|" + item)
            screen.addstr(line + 2 * multiple + integer, remainder, "+" + '-' * value_len[index])
        screen.addstr(line + 1 * multiple - 1, sum(value_len[0:len(keys)]) - line_len * (multiple - 1), "+")
        screen.addstr(line + 2 * multiple - 1, sum(value_len[0:len(keys)]) - line_len * (multiple - 1), "|")
        screen.addstr(line + 3 * multiple - 1, sum(value_len[0:len(keys)]) - line_len * (multiple - 1), "+")

        line += 3 * multiple
        for instance in papi:
            index = 0
            if line + multiple > page_len:
                break
            while index < len(keys):
                integer, remainder = divmod(sum(value_len[0:index]), line_len)
                screen.addstr(line + integer, remainder, "|" + str(instance[values[index]]))
                index += 1
            screen.addstr(line + 1 * multiple - 1, sum(value_len[0:len(keys)]) - line_len * (multiple - 1), "|")
            line += 1 * multiple
        if line + multiple > page_len:
                time.sleep(1)
                continue
        for index, item in enumerate(keys):
            integer, remainder = divmod(sum(value_len[0:index]), line_len)
            screen.addstr(line + integer, remainder, "+" + '-' * value_len[index])
        screen.addstr(line + 1 * multiple - 1, sum(value_len[0:len(keys)]) - line_len * (multiple - 1), "+")
        screen.refresh()
        time.sleep(1)


if __name__ == '__main__':
    try:
        screen = curses.initscr()

        thread.start_new_thread(url_report, (screen,))
        x = 0
        while x != ord('q'):
            x = screen.getch()
        curses.endwin()
    except Exception, e:
        print e
curses.endwin()

