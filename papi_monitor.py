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

locale.setlocale(locale.LC_ALL, "")

message = 'function.py [(int)START] [(int)END] [(int)SORT] \n \
      START > 0 \n \
      SORT in [1, 2, 3]'

parser = optparse.OptionParser(usage=message)
(opts, args) = parser.parse_args()

START = int(sys.argv[1])
END = int(sys.argv[2])
SORT = int(sys.argv[3])


class PapiMonitor():
    TOP = 0
    NUM = 0
    UP = -1
    DOWN = 1
    REQUESTLONG = 0

    def url_report(self, screen):
        keys = ["实例id", "ip", "已建数据库", "实际建数据库", "数据库资源数误差", "磁盘大小", "磁盘使用量", "磁盘数用率"]
        value_len = []
        for key in keys:
            value_len.append(int(round(len(key) * 0.8)))
        while True:
            screen.clear()
            url = "http://192.168.194.129:8087/?action=desc_instance_used&begin=%s&end=%s&sort=%s" % (START, END+1, SORT)
            papi = urllib2.urlopen(url, timeout=10).read()
            papi = json.loads(papi)
            keys = [" 实例id ", " ip ", " 已建数据库 ", " 实际建数据库 ", " 数据库资源数误差 ", " 磁盘大小 ", " 磁盘使用量 ", " 磁盘数用率 "]
            values = ["id", "ip", "quota_db_num", "actually_use_db", "db_differ_num", "capacity_total", "capacity_used", "ratio_used"]
            page_len, line_len = screen.getmaxyx()#获取屏幕显示尺寸
            line = 1
            self.REQUESTLONG = len(papi)
            for instance in papi:
                index = 0
                while index < len(keys):
                    if len(str(instance[values[index]])) > value_len[index]:
                        value_len[index] = len(str(instance[values[index]])) + 2
                    index += 1
            multiple = int(math.ceil(sum(value_len[0:len(keys)]) / float(line_len)))
            screen.addstr(line, 1, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            line += 1
            if line + 4 * multiple > page_len:
                screen.addstr(1, 1, "哥， 窗口也太小了吧...")
                screen.refresh()
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

            self.NUM = (page_len - 4 * multiple - 2) / multiple
            if self.NUM < 0:
                self.NUM = 0
            screen.addstr(1, 25, "NUM:" + str(self.NUM) + " REQUESTLONG:" + str(self.REQUESTLONG) + " TOP:" + str(self.TOP))
#            end = self.NUM + self.TOP
            for instance in papi[self.TOP:self.NUM + self.TOP]:
                index = 0
                while index < len(keys):
                    integer, remainder = divmod(sum(value_len[0:index]), line_len)
                    screen.addstr(line + integer, remainder, "|" + str(instance[values[index]]))
                    index += 1
                screen.addstr(line + 1 * multiple - 1, sum(value_len[0:len(keys)]) - line_len * (multiple - 1), "|")
                line += 1 * multiple

            for index, item in enumerate(keys):
                integer, remainder = divmod(sum(value_len[0:index]), line_len)
                screen.addstr(line + integer, remainder, "+" + '-' * value_len[index])
            screen.addstr(line + 1 * multiple - 1, sum(value_len[0:len(keys)]) - line_len * (multiple - 1), "+")
            screen.refresh()
            time.sleep(1)

    def updown(self, increment):

        # paging
        if increment == self.UP and self.TOP > 0 and self.REQUESTLONG > self.NUM and self.NUM > 0:
            self.TOP += self.UP
            return
        elif increment == self.DOWN and self.REQUESTLONG > self.TOP + self.NUM and self.NUM > 0:
            self.TOP += self.DOWN
            return

    def restoreScreen(self):
        curses.initscr()
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    # catch any weird termination situations
    def __del__(self):
        self.restoreScreen()


if __name__ == '__main__':
    try:
        screen = curses.initscr()
        monitor = PapiMonitor()
        thread.start_new_thread(monitor.url_report, (screen,))
        x = 0
        while x != ord('q'):
            x = screen.getch()
            if x == ord('w'):
                monitor.updown(monitor.UP)
            elif x == ord('s'):
                monitor.updown(monitor.DOWN)
        curses.endwin()
    except Exception, e:
        print e


