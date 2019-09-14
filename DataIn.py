import os
import subprocess
import re
import time
from multiprocessing import Process, Manager
import pprint


def find_wifi(interface, dic):
    table = ''
    timeout = 60
    temp = {}
    table_start = re.compile('\sCH')
    line_start = re.compile('[A-Z0-9]{2}:[A-Z0-9]{2}:[A-Z0-9]{2}:[A-Z0-9]{2}:[A-Z0-9]{2}:[A-Z0-9]{2}')
    start_time = time.time()

    airodump = subprocess.Popen(['airodump-ng -c 10', interface], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1)

    while time.time() < start_time + timeout:
        line = airodump.stdout.readline().strip('\n')
        if table_start.match(line):
            print(temp)
            temp = {}

        line = [x for x in line.split(' ') if x != '']
        if line != [] and line_start.match(line[0]):
            if line[0] == "20:A6:CD:53:E9:C3":
                temp[line[0]] = [line[1], line[-1], line[5]]

    airodump.terminate()


if __name__ == '__main__':
    manager = Manager()

    d = manager.dict()

    p1 = Process(target=find_wifi, args=('wlp0s20f3', d))

    p1.start()

    #for i in range(60):
    #    print(d)
    #    time.sleep(1)
