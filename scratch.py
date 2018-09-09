#from pygame import mixer
# Load the required library
from node import Cluster
import time
import logging
import time
import random
import opc
import color_utils
import math
import sys
import random
import optparse
try:
    import json
except ImportError:
    import simplejson as json
import opc
import color_utils

num_nodes = 25
all_nodes = Cluster (num_nodes,0.01)
all_nodes.start()

def main():
    #mixer.init()
    #mixer.music.load('/home/maayand/Downloads/Wonderland_background.mp3')
    #mixer.music.play(-1)


    ADDRESS = 'localhost:7890'

    # Create a client object
    client = opc.Client(ADDRESS)

    # Test if it can connect
    if client.can_connect():
        print
        'connected to %s' % ADDRESS
    else:
        # We could exit here, but instead let's just print a warning
        # and then keep trying to send pixels in case the server
        # appears later
        print
        'WARNING: could not connect to %s' % ADDRESS


    # Send pixels forever

    print('    sending pixels forever (control-c to exit)...')
    print('')

def _get_cartesian_layout():
    coordinates = []
    lines = []
    layout_json = '/home/maayand/Documents/Projects/openpixelcontrol/layouts/insomniacs.json'

    for item in json.load(open(layout_json)):
        if 'point' in item:
            coordinates.append(tuple(item['point']))
        if 'line' in item:
            lines.append(tuple(item['line']))

    return coordinates

def raver_palid(address='192.168.0.8:7890', fps=100, n_pixels = 25):
    start_time = time.time()
    client = opc.Client('localhost:7890')

    # how many sine wave cycles are squeezed into our n_pixels
    # 24 happens to create nice diagonal stripes on the wall layout
    freq_r = 24
    freq_g = 24
    freq_b = 24

    # how many seconds the color sine waves take to shift through a complete cycle
    speed_r = 7
    speed_g = -13
    speed_b = 19

    for i in inf_loop(360 * 2, 1):
        t = (time.time() - start_time) * 5
        pixels = []
        for ii in range(n_pixels):
            pct = (ii / n_pixels)
            # diagonal black stripes
            pct_jittered = (pct * 77) % 37
            blackstripes = color_utils.cos(pct_jittered, offset=t * 0.05, period=1, minn=-1.5, maxx=1.5)
            blackstripes_offset = color_utils.cos(t, offset=0.9, period=60, minn=-0.5, maxx=3)
            blackstripes = color_utils.clamp(blackstripes + blackstripes_offset, 0, 1)
            # 3 sine waves for r, g, b which are out of sync with each other
            r = blackstripes * color_utils.remap(math.cos((t / speed_r + pct * freq_r) * math.pi * 2), -1, 1, 0, 256)
            g = blackstripes * color_utils.remap(math.cos((t / speed_g + pct * freq_g) * math.pi * 2), -1, 1, 0, 256)
            b = blackstripes * color_utils.remap(math.cos((t / speed_b + pct * freq_b) * math.pi * 2), -1, 1, 0, 256)
            pixels.append((r, g, b))
            all_nodes.setNodeColor(int(ii), int(r), int(g), int(b))

        client.put_pixels(pixels, channel=0)
        time.sleep(1 / fps)

def _get_polar_layout():
    return [[math.sqrt(x ** 2 + y ** 2), math.atan2(y, x), z] for x, y, z in _get_cartesian_layout()]


def inf_loop(counter, increment = 1):
    while True:
        for i in range(0, counter, increment):
            yield i


def cone(address='192.168.0.8:7890', fps=100):
    client = opc.Client('localhost:7890')
    for i in inf_loop(360 * 2, 1):
        pixels = []
        for x, y, z in _get_cartesian_layout():
            midx = math.sin(i * math.pi / 180)
            midy = math.cos(i * math.pi / 180)
            dist = math.sqrt((midx - x) ** 2 + (midy - y) ** 2)
            val = dist * 255 / 3
            pixels.append((val, 0, 128))
        client.put_pixels(pixels, channel=0)
        time.sleep(1 / fps)


def shift(arr, count=1):
    return arr[-count:] + arr[:-count]


def rainbow_stream():
    for i in range(3):
        for j in range(255):
            yield shift((255 - j, j, 0), i)


def play_rainbow(address='192.168.0.8:7890', fps=100):
    client = opc.Client('localhost:7890')
    # play with this constant for "color distance"
    # at 200, the inner moon would take a different color to the outer one
    # at 10, the transition would take a lot longer
    bands = [math.floor(x[0] * 200) for x in _get_polar_layout()]
    buffer = [x for x in rainbow_stream()]
    for i in inf_loop(360):
        pixels = [buffer[bands[x]] for x in range(len(bands))]
        client.put_pixels(pixels)
        if i % 1 == 0:
            buffer = shift(buffer)  # change the shift to -1 for an ingoing action
        time.sleep(1 / fps)


def counter_clockwise_rainbow(address='192.168.0.8:7890', fps=100):
    client = opc.Client('localhost:7890')
    buffer = [x for x in rainbow_stream()]
    slices = [math.floor(x[1] * len(buffer) / (2 * math.pi)) for x in _get_polar_layout()]
    for i in inf_loop(360):
        pixels = [buffer[slices[x]] for x in range(len(slices))]
        client.put_pixels(pixels)
        if i % 1 == 0:  # pick a higher mod to slow the animation down (2 would halve the speed etc)
            buffer = shift(buffer)  # to make this go clockwise, change the shift count to -1
        time.sleep(1 / fps)


if __name__ == "__main__":
    #raver_palid()
    #counter_clockwise_rainbow()
    #play_rainbow()
    cone()


