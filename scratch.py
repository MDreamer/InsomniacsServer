import pygame
#from pygame import mixer
import os
import random

from node import Cluster
from os import listdir
from os.path import isfile, join
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

#creates a dummy display to be used by pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"

_songs = []

#Add a flag indicating which song is currently playing:
_currently_playing_song = None


try:
    import json
except ImportError:
    import simplejson as json
import opc
import color_utils
import threading

aniIndex = 0  # Index that indicates which animation to run:
exitFlag = 0

# freda() #0
# raver_palid() #1
# play_rainbow() #2
# cone() #3
# counter_clockwise_rainbow() #4


num_nodes = 25
all_nodes = Cluster(num_nodes, 0.01)
all_nodes.start()
ADDRESS = 'localhost:7890'
client = opc.Client(ADDRESS)

def main():
    # mixer.init()
    # mixer.music.load('/home/maayand/Downloads/Wonderland_background.mp3')
    # mixer.music.play(-1)

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


def raver_palid(address='192.168.0.8:7890', fps=100, n_pixels=25):
    global aniIndex, client
    print ("Raver")
    start_time = time.time()
    #client = opc.Client('localhost:7890')

    # how many sine wave cycles are squeezed into our n_pixels
    # 24 happens to create nice diagonal stripes on the wall layout
    freq_r = 24
    freq_g = 24
    freq_b = 24

    # how many seconds the color sine waves take to shift through a complete cycle
    speed_r = 7
    speed_g = -13
    speed_b = 19

    while aniIndex == 1:
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


def inf_loop(counter, in_aniIndex, increment=1):
    global aniIndex
    while (aniIndex == in_aniIndex):
        for i in range(0, counter, increment):
            yield i


def cone(address='192.168.0.8:7890', fps=100):
    global aniIndex, client
    print("cone")
    #client = opc.Client('localhost:7890')
    for i in inf_loop(360 * 2, aniIndex, 1):
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
    global aniIndex, client
    print("Rainbow")
    #client = opc.Client('localhost:7890')
    # play with this constant for "color distance"
    # at 200, the inner moon would take a different color to the outer one
    # at 10, the transition would take a lot longer
    bands = [math.floor(x[0] * 200) for x in _get_polar_layout()]
    buffer = [x for x in rainbow_stream()]
    for i in inf_loop(360 * 2, aniIndex, 1):
        pixels = [buffer[bands[x]] for x in range(len(bands))]
        client.put_pixels(pixels)
        if i % 1 == 0:
            buffer = shift(buffer)  # change the shift to -1 for an ingoing action
        time.sleep(1 / fps)


def counter_clockwise_rainbow(address='192.168.0.8:7890', fps=100):
    global aniIndex, client
    print("ccw rainbow")
    #client = opc.Client('localhost:7890')
    buffer = [x for x in rainbow_stream()]
    slices = [math.floor(x[1] * len(buffer) / (2 * math.pi)) for x in _get_polar_layout()]
    for i in inf_loop(360 * 2,aniIndex, 1):
        pixels = [buffer[slices[x]] for x in range(len(slices))]
        client.put_pixels(pixels)
        if i % 1 == 0:  # pick a higher mod to slow the animation down (2 would halve the speed etc)
            buffer = shift(buffer)  # to make this go clockwise, change the shift count to -1
        time.sleep(1 / fps)

'''
def radius(coord):
    x = coord[0]
    y = coord[1]
    R = math.sqrt(x ** 2 + y ** 2)
    return R


def pixel_colors(t, state, coord, ii):
    start = time.time()
    while t - start < 30:
        r, g, b = animations.outward_swell(t, coord)
        my_pixels.append((r, g, b))

def outward_swell(t,coord,my_pixels):
    R = radius(coord)
    g=0.2
    b=color_utils.cos(R,offset=t/8,period=10,minn=0.3,maxx=0.45)
    r=color_utils.cos(R,offset=t/8,period=10,minn=0,maxx=0.50)
    r, g, b = color_utils.gamma((r, g, b), 0.7)
    r,g,b=[color_utils.remap(color,0,1,0,255) for color in (r,g,b)]
    my_pixels.append((r, g, b))

def freda1():
    last_time = time.time()
    start_time = time.time()
    print(start_time)
    interval = 10
    state = 0

    num_pixels = len(coordinates)

    R = [radius(coord) for coord in coordinates]

    moon_id = []
    planets_id = []

    R_max = max(R)
    R_min = min(R)

    # for i in range(len(R)):
    #     if 0.7<R[i]<1.3:
    #         print (R[i])
    #         planets_id.append(i)
    #     else:
    #         moon_id.append(i)

    fps = 100
    while aniIndex == 0:
        my_pixels = []
        t = time.time()
        if t - start_time > interval:
            start_time = t
            print(state)
            if state == 0:
                state = 1
            else:
                state = 0
        if state == 0:
            [animations.outward_swell(t, coord, my_pixels) for coord in coordinates]
        if state == 1:
            [animations.moons_and_planets_blink(t, coord, my_pixels, R_min, R_max) for coord in coordinates]
        if client.put_pixels(my_pixels, channel=0):
            print
            'sent'
        else:
            print
            'not connected'
        time.sleep(1 / fps)
'''

# aniTime is the time that is dedicated per animation in minutes, default is 30min
class AnimationCycleThread(threading.Thread):
    def __init__(self, aniTime=30):
        threading.Thread.__init__(self)
        self.aniTime = aniTime

    def run(self):
        print ("Starting AnimationCycleThread")
        self.play_time(self.aniTime)
        print ("Exiting AnimationCycleThread")

    def play_time(self, delay):
        global aniIndex
        while exitFlag != 1:
            #time.sleep(self.aniTime * 60)
            time.sleep(10)
            aniIndex = aniIndex + 1
            aniIndex = aniIndex % 5


# aniTime is the time that is dedicated per animation in minutes, default is 30min
class AnimationPlayThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print ("Starting AnimationPlayThread")
        self.play_time()
        print ("Exiting AnimationPlayThread")

    def play_time(self):
        global aniIndex, _currently_playing_song, _songs
        while exitFlag != 1:
            #if aniIndex == 0:
            #    freda()
            if aniIndex == 1:
                raver_palid()
            if aniIndex == 2:
                play_rainbow()
            if aniIndex == 3:
                cone()
            if aniIndex == 4:
                counter_clockwise_rainbow()
            time.sleep(1)
            print (aniIndex)


# And write a function that chooses a different song randomly that gets called each time the SONG_END event is fired:
def play_a_different_song():
    global _currently_playing_song, _songs
    next_song = random.choice(_songs)
    while next_song == _currently_playing_song:
        next_song = random.choice(_songs)
    _currently_playing_song = next_song
    print(str(_currently_playing_song) + " is played now...")
    pygame.mixer.music.load(next_song)
    pygame.mixer.music.play(1)


if __name__ == "__main__":
    music_path = '/home/maayand/Downloads/music'

    client = opc.Client('localhost:7890')

    for file in os.listdir(music_path):
        if file.endswith(".mp3"):
            print(os.path.join(music_path, file))
            if file != None and file != "":
                _songs.append(os.path.join(music_path, file))


    pygame.init()
    pygame.mixer.init()

    SONG_END = pygame.USEREVENT + 1

    pygame.mixer.music.set_endevent(SONG_END)
    pygame.mixer.music.load(_songs[0])
    pygame.mixer.music.play(1)

    # Create new thread
    cycleAni = AnimationCycleThread(30)
    playAni = AnimationPlayThread()

    # Start new Threads
    cycleAni.start()
    playAni.start()

    while True:
        for event in pygame.event.get():
            if event.type == SONG_END:
                print(str(_currently_playing_song) + " the song ended!")
                play_a_different_song()
                time.sleep(1)

    # freda() #0
    # raver_palid() #1
    # play_rainbow() #2
    # cone() #3
    # counter_clockwise_rainbow() #4
