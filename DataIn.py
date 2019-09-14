import os
import subprocess
import re
import time
from multiprocessing import Process, Manager
import pprint
import datetime
import copy

def find_wifi(interface, d):
    table = ''
    timeout = 99999
    temp = {}
    table_start = re.compile('\sCH')
    line_start = re.compile('[A-Z0-9]{2}:[A-Z0-9]{2}:[A-Z0-9]{2}:[A-Z0-9]{2}:[A-Z0-9]{2}:[A-Z0-9]{2}')
    start_time = time.time()

    airodump = subprocess.Popen(['airodump-ng', interface, '-c', '153'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1)

    while time.time() < start_time + timeout:

        line = airodump.stdout.readline().strip('\n')

        #print(line)

        if table_start.match(line):
            #print(datetime.datetime.now())
            #pprint.pprint(d)
            d = {}

        line = [x for x in line.split(' ') if x != '']
        if line != [] and line_start.match(line[0]):
            #if False or line[0] == "C0:EE:FB:5B:1E:92":
            d[line[0]] = [line[1], line[-1], line[5]]

    airodump.terminate()

def get_node_data(d):

    start_time = time.time()

    accumulated_data = {}

    while time.time() - start_time < 1:
        print(d)

        for a in d:
            if a not in accumulated_data:
                accumulated_data[a] = []

            accumulated_data[a].append(d[a])

    print(accumulated_data)

if __name__ == '__main__':
    manager = Manager()

    d = manager.dict()

    p1 = Process(target=find_wifi, args=('wlp0s20f3', d))

    p1.start()

    while True:
        get_node_data(d)

    #for i in range(60):
    #    print(d)
    #    time.sleep(1)
