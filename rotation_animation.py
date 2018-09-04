from __future__ import division
import time
import math
import sys

import opc
import color_utils


client = opc.Client('192.168.0.8:7890')
if client.can_connect():
    print('    connected to %s' % IP_PORT)
else:
    # can't connect, but keep running in case the server appears later
    print('    WARNING: could not connect to %s' % IP_PORT)
print('')

# -------------------------------------------------------------------------------
# send pixels

print('    sending pixels forever (control-c to exit)...')
print('')

fps = 60  # frames per second

def infloop(counter, increment: 1):
    while True:
        for it in range(0, counter, increment):
            yield it


pts = [
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

start_time = time.time()
for i in infloop(360, 2):
    pixels = []
    for p in pts:
        midx = math.sin(i * math.pi / 180)
        midy = math.cos(i * math.pi / 180)
        dist = math.sqrt((midx - p[0]) ** 2 + (midy - p[1]) ** 2)
        val = dist * 255 / 3
        pixels.append((val, 0, 128))
    client.put_pixels(pixels, channel=0)
    time.sleep(1 / fps)
