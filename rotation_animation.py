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


def inf_loop(counter, increment: 1):
    while True:
        for i in range(0, counter, increment):
            yield i


# angles
_7th = 2 * math.pi / 7


class Band(object):
    inner = 2000
    mid = 4000
    outer = 6000


# heights
class Height(object):
    bot_duo = 1010.11
    top_duo = 2420.13
    moon = 1494.45
    bot_trio = 1010.11
    top_trio = 2692.5


def inner_moon(segment):
    return [(Band.inner, segment * _7th, Height.moon)]


def outer_moon(segment):
    return [(Band.outer, segment * _7th, Height.moon)]


def planet(segment):
    return [(Band.mid, segment * _7th, Height.bot_duo)]


def pyramid(segment):
    return [((Band.inner + Band.mid) / 2, segment * _7th, Height.bot_trio),
            (Band.mid, segment * _7th, Height.top_trio),
            ((Band.mid + Band.outer) / 2, segment * _7th, Height.bot_trio)]


def totem(segment):
    return [(Band.mid, segment * _7th, Height.bot_duo),
            (Band.mid, segment * _7th, Height.top_duo)]


def get_polars():
    return totem(0) + outer_moon(0) + \
           inner_moon(1) + planet(1) + outer_moon(1) + \
           pyramid(2) + outer_moon(2) + \
           inner_moon(3) + totem(3) + outer_moon(3) + \
           pyramid(4) + outer_moon(4) + \
           planet(5) + outer_moon(5) + \
           inner_moon(6) + pyramid(6) + outer_moon(6)


def get_cartesian_pts(scale):
    return [(x[0] * math.cos(x[1]) / scale, x[0] * math.sin(x[1]) / scale, x[2] / scale) for x in get_polars()]


def get_layout(scale):
    return json.dumps([{"point": [round(x[0], 2), round(x[1], 2), round(x[2], 2)]} for x in get_cartesian_pts(scale)])


def main():
    client = _connect(address)
    start_time = time.time()
    for i in inf_loop(360, 2):
        pixels = []
        for p in pts:
            midx = math.sin(i * math.pi / 180)
            midy = math.cos(i * math.pi / 180)
            dist = math.sqrt((midx - p[0]) ** 2 + (midy - p[1]) ** 2)
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
    bands = [math.floor(x[0] // 25) for x in get_polars()]
    buffer = [x for x in rainbow_stream()]
    while True:
        pixels = [buffer[bands[x]] for x in range(len(bands))]
        client.put_pixels(pixels)
        buffer = shift(buffer)
        time.sleep(1/fps)


def clockwise_rainbow(address='192.168.0.8:7890', fps=100):
    client = _connect(address)
    buffer = [x for x in rainbow_stream()]
    slices = [math.floor(x[1] * len(buffer) / (2 * math.pi)) for x in get_polars()]
    while True:
        pixels = [buffer[slices[x]] for x in range(len(slices))]
        client.put_pixels(pixels)
        buffer = shift(buffer)
        time.sleep(1/fps)


if __name__ == "__main__":
    main()
