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
    SHOWNUM = 0
    UP = -1
    DOWN = 1
    INSTANCENUM = 0
    KEYS = ["实例id", "ip", "已建数据库", "实际建数据库", "数据库资源数误差", "磁盘大小", "磁盘使用量", "磁盘数用率"]
    VALUES = ["id", "ip", "quota_db_num", "actually_use_db", "db_differ_num", "capacity_total", "capacity_used", "ratio_used"]

    def run_monitor(self, screen):
        value_long = []
        value_long = self.get_every_key_long(value_long)

        while True:
            try:
                screen.clear()
                row_index = 1
                screen_high, screen_width = screen.getmaxyx()#获取屏幕显示尺寸
                instance_list = self.get_monitor_info()
                self.INSTANCENUM = len(instance_list)
                value_long = self.get_max_value_long(instance_list, value_long)
                one_instance_rows = int(math.ceil(sum(value_long[0:len(self.KEYS)]) / float(screen_width)))

                screen.addstr(row_index, 1, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
                row_index += 1
                if row_index + 4 * one_instance_rows > screen_high:
                    screen.addstr(1, 1, "哥， 窗口也太小了吧...")
                    screen.refresh()
                    time.sleep(1)
                    continue

                self.refresh_init_info(value_long, screen_width, one_instance_rows)
                row_index += 3 * one_instance_rows
                self.SHOWNUM = (screen_high - 4 * one_instance_rows - 2) / one_instance_rows
                if self.SHOWNUM < 0:
                    self.SHOWNUM = 0
                screen.addstr(1, 25, "SHOWNUM:" + str(self.SHOWNUM) + " INSTANCENUM:" + str(self.INSTANCENUM) + " TOP:" + str(self.TOP))

                row_index = self.refresh_instance_info(instance_list, value_long, screen_width, row_index, one_instance_rows)

                self.refresh_end_info(value_long, screen_width, row_index, one_instance_rows)
                screen.refresh()
                time.sleep(1)
            except Exception, e:
                screen.addstr(0, 0, str(e))
                screen.refresh()
                time.sleep(1)

    def refresh_instance_info(self, instance_list, value_long, screen_width, row_index, one_instance_rows):
        for instance in instance_list[self.TOP:self.SHOWNUM + self.TOP]:
            index = 0
            while index < len(self.KEYS):
                integer, remainder = divmod(sum(value_long[0:index]), screen_width)
                screen.addstr(row_index + integer, remainder, "|" + str(instance[self.VALUES[index]]))
                index += 1
            screen.addstr(row_index + 1 * one_instance_rows - 1, sum(value_long[0:len(self.KEYS)]) - screen_width * (one_instance_rows - 1), "|")
            row_index += 1 * one_instance_rows
        return row_index

    def refresh_end_info(self, value_long, screen_width, row_index, one_instance_rows):
        for index, item in enumerate(self.KEYS):
            integer, remainder = divmod(sum(value_long[0:index]), screen_width)
            screen.addstr(row_index + integer, remainder, "+" + '-' * value_long[index])
        screen.addstr(row_index + 1 * one_instance_rows - 1, sum(value_long[0:len(self.KEYS)]) - screen_width * (one_instance_rows - 1), "+")

    def refresh_init_info(self, value_long, screen_width, one_instance_rows):
        row_index = 2
        for index, item in enumerate(self.KEYS):
            integer, remainder = divmod(sum(value_long[0:index]), screen_width)
            screen.addstr(row_index + integer, remainder, "+" + '-' * value_long[index])
            screen.addstr(row_index + 1 * one_instance_rows + integer, remainder, "|" + item)
            screen.addstr(row_index + 2 * one_instance_rows + integer, remainder, "+" + '-' * value_long[index])
        screen.addstr(row_index + 1 * one_instance_rows - 1, sum(value_long[0:len(self.KEYS)]) - screen_width * (one_instance_rows - 1), "+")
        screen.addstr(row_index + 2 * one_instance_rows - 1, sum(value_long[0:len(self.KEYS)]) - screen_width * (one_instance_rows - 1), "|")
        screen.addstr(row_index + 3 * one_instance_rows - 1, sum(value_long[0:len(self.KEYS)]) - screen_width * (one_instance_rows - 1), "+")

    def get_max_value_long(self, instance_list, value_long):
        for instance in instance_list:
            index = 0
            while index < len(self.KEYS):
                if len(str(instance[self.VALUES[index]])) > value_long[index]:
                    value_long[index] = len(str(instance[self.VALUES[index]])) + 2
                index += 1
        return value_long

    def get_every_key_long(self, value_long):
        for key in self.KEYS:
            value_long.append(int(round(len(key) * 0.8)))
        return value_long

    def get_monitor_info(self):
        url = "http://192.168.194.129:8087/?action=desc_instance_used&begin=%s&end=%s&sort=%s" % (START, END+1, SORT)
        papi = urllib2.urlopen(url, timeout=10).read()
        instance_list = json.loads(papi)
        return instance_list

    def updown(self, increment):
        # paging
        if increment == self.UP and self.TOP > 0 and self.INSTANCENUM > self.SHOWNUM and self.SHOWNUM > 0:
            self.TOP += self.UP
            return
        elif increment == self.DOWN and self.INSTANCENUM > self.TOP + self.SHOWNUM and self.SHOWNUM > 0:
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
        thread.start_new_thread(monitor.run_monitor, (screen,))
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


