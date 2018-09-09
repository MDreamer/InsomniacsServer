from __future__ import division

import sys
import time
import math
import opc
import json


def _connect(address):
    client = opc.Client(address)
    if client.can_connect():
        print('    connected to %s' % address)
    else:
        # can't connect, but keep running in case the server appears later
        print('    WARNING: could not connect to %s' % address)
    print('')

    return client


def _get_cartesian_layout():
    return [
        [0.00, 1.71, 0.43],
        [0.98, 1.40, 0.43],
        [1.69, 0.30, 0.43],
        [1.10, -1.31, 0.43],
        [0.00, -1.71, 0.43],
        [-1.21, -1.21, 0.43],
        [-1.48, 0.86, 0.43],
        [0.00, 1.14, 0.29],
        [-0.21, 1.26, 0.77],
        [-0.42, 1.38, 0.29],
        [0.66, 0.94, 0.29],
        [1.13, 0.20, 0.29],
        [1.13, 0.20, 0.69],
        [0.73, -0.88, 0.29],
        [0.97, -0.83, 0.77],
        [1.21, -0.79, 0.29],
        [0.00, -1.14, 0.29],
        [-0.81, -0.81, 0.29],
        [-1.04, -0.75, 0.77],
        [-1.27, -0.68, 0.29],
        [-0.99, 0.57, 0.29],
        [-0.99, 0.57, 0.69],
        [0.33, 0.47, 0.43],
        [0.37, -0.44, 0.43],
        [-0.49, 0.29, 0.43]
    ]


def _get_polar_layout():
    return [[math.sqrt(x ** 2 + y ** 2), math.atan2(y, x), z] for x, y, z in _get_cartesian_layout()]


def inf_loop(counter, increment = 1):
    while True:
        for i in range(0, counter, increment):
            yield i


def cone(address='192.168.0.8:7890', fps=100):
    client = _connect(address)
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
    client = _connect(address)
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
    client = _connect(address)
    buffer = [x for x in rainbow_stream()]
    slices = [math.floor(x[1] * len(buffer) / (2 * math.pi)) for x in _get_polar_layout()]
    for i in inf_loop(360):
        pixels = [buffer[slices[x]] for x in range(len(slices))]
        client.put_pixels(pixels)
        if i % 1 == 0:  # pick a higher mod to slow the animation down (2 would halve the speed etc)
            buffer = shift(buffer)  # to make this go clockwise, change the shift count to -1
        time.sleep(1 / fps)


if __name__ == "__main__":
    cone()
