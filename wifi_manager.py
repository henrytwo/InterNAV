import os
import subprocess
import re
import time
from multiprocessing import Process, Manager
import pprint
import datetime
import copy

def dump_aps(interface):
    table = ''
    timeout = 1

    table_start = re.compile('\sCH')
    line_start = re.compile('[A-Z0-9]{2}:[A-Z0-9]{2}:[A-Z0-9]{2}:[A-Z0-9]{2}:[A-Z0-9]{2}:[A-Z0-9]{2}')
    start_time = time.time()

    airodump = subprocess.Popen(['airodump-ng', interface, '-c', '1,11'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1)

    accumulator = {}

    while time.time() - start_time < timeout:

        line = airodump.stdout.readline().strip('\n')

        line = [x for x in line.split(' ') if x != '']
        if line != [] and line_start.match(line[0]):

            if line[0] not in accumulator:
                accumulator[line[0]] = []

            accumulator[line[0]].append([line[1], line[-1], line[5]])

    final = {}

    for a in accumulator:
        s = 0

        for z in accumulator[a]:

            try:
                s += int(z[0])
            except:
                pass


        final[a] = abs(s / len(accumulator[a]))

    airodump.terminate()

    return final

if __name__ == '__main__':

    while True:
        try:

            pprint.pprint(dump_aps('wlp0s20f3mon'))
        except:
            pass