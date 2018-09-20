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
run_sim = True
if (run_sim == True):
    client = opc.Client(ADDRESS)

layout_json_path = "C:\\Users\\maayan.dermer\\Downloads\\InsomniacsServer-master\\InsomniacsServer-master\\layouts\\insomniacs.json"

def _get_cartesian_layout():
    global layout_json_path
    coordinates = []
    lines = []
    
    for item in json.load(open(layout_json_path)):
        if 'point' in item:
            coordinates.append(tuple(item['point']))
        if 'line' in item:
            lines.append(tuple(item['line']))

    return coordinates


def raver_palid(fps=100, n_pixels=25):
    global aniIndex, client
    print ("Raver")
    start_time = time.time()

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

        if (run_sim == True):
            client.put_pixels(pixels, channel=0)

        time.sleep(1 / fps)


def _get_polar_layout():
    return [[math.sqrt(x ** 2 + y ** 2), math.atan2(y, x), z] for x, y, z in _get_cartesian_layout()]


def inf_loop(counter, in_aniIndex, increment=1):
    global aniIndex
    while (aniIndex == in_aniIndex):
        for i in range(0, counter, increment):
            yield i


def cone(fps=100):
    global aniIndex, client
    print("cone")
    
    for i in inf_loop(360 * 2, aniIndex, 1):
        pixels = []
        for x, y, z in _get_cartesian_layout():
            midx = math.sin(i * math.pi / 180)
            midy = math.cos(i * math.pi / 180)
            dist = math.sqrt((midx - x) ** 2 + (midy - y) ** 2)
            val = dist * 255 / 3
            pixels.append((val, 0, 128))
        
        if (run_sim == True):
            client.put_pixels(pixels, channel=0)

        time.sleep(1 / fps)


def shift(arr, count=1):
    return arr[-count:] + arr[:-count]


def rainbow_stream():
    for i in range(3):
        for j in range(255):
            yield shift((255 - j, j, 0), i)

def play_rainbow(fps=100):
    global aniIndex, client
    print("Rainbow")
    
    # play with this constant for "color distance"
    # at 200, the inner moon would take a different color to the outer one
    # at 10, the transition would take a lot longer
    bands = [math.floor(x[0] * 200) for x in _get_polar_layout()]
    buffer = [x for x in rainbow_stream()]
    for i in inf_loop(360 * 2, aniIndex, 1):
        pixels = [buffer[bands[x]] for x in range(len(bands))]
        if (run_sim == True):
            client.put_pixels(pixels)
        if i % 1 == 0:
            buffer = shift(buffer)  # change the shift to -1 for an ingoing action
        time.sleep(1 / fps)


def counter_clockwise_rainbow(fps=100):
    global aniIndex, client
    print("ccw rainbow")
    
    buffer = [x for x in rainbow_stream()]
    slices = [math.floor(x[1] * len(buffer) / (2 * math.pi)) for x in _get_polar_layout()]
    for i in inf_loop(360 * 2,aniIndex, 1):
        pixels = [buffer[slices[x]] for x in range(len(slices))]
        if (run_sim == True):
            client.put_pixels(pixels)
        if i % 1 == 0:  # pick a higher mod to slow the animation down (2 would halve the speed etc)
            buffer = shift(buffer)  # to make this go clockwise, change the shift count to -1
        time.sleep(1 / fps)

def radius(coord):
    x = coord[0]
    y = coord[1]
    R = math.sqrt(x ** 2 + y ** 2)
    return R

def find_theta(coord):
    x,y,z=coord
    R=radius(coord)
    theta = math.acos(y/R)
    if x < 0:
        theta=math.radians(360)-theta
    return theta


def outward_swell(fps=100, in_aniIndex = 0):
    global aniIndex, client, coordinates
    pixels = []
    print("outward_swell")
    while (aniIndex == in_aniIndex):
        t=time.time()
        for coord in coordinates:
            R = radius(coord)
            g=0.2
            b=color_utils.cos(R,offset=t/8,period=10,minn=0.3,maxx=0.45)
            r=color_utils.cos(R,offset=t/8,period=10,minn=0,maxx=0.50)
            r, g, b = color_utils.gamma((r, g, b), 0.7)
            r,g,b=[color_utils.remap(color,0,1,0,255) for color in (r,g,b)]
            pixels.append((r, g, b))
            
            if (run_sim == True):
                client.put_pixels(pixels)

        time.sleep(1 / fps)


def moons_and_planets_blink(t, coord, my_pixels, R_min, R_max, fps=100): #alternate blinking moons and planets
    R = radius(coord)
    x,y,z=coord
    theta=find_theta(coord)
    R=color_utils.remap(R,R_min,R_max,0,6)
    if 2.5 < R < 5.5: #planets
        r=color_utils.cos(t,offset=1,period=10,minn=10,maxx=100)
        g=color_utils.cos(t,offset=1,period=10,minn=10,maxx=100)
        b=color_utils.cos(t,offset=1,period=10,minn=10,maxx=150)
        r,g,b = [color_utils.remap(color, 0, 255, 0, 1) for color in (r, g, b)]
        r,g,b=color_utils.gamma((r,g,b),0.8)
        r,g,b=[color_utils.remap(color, 0, 1, 0, 255) for color in (r, g, b)]
    elif R > 5.5 or R<2.5:
        r=color_utils.cos(t,offset=0.5,period=10,minn=0,maxx=0.6)
        g=0.2
        b=color_utils.cos(t,offset=0.5,period=10,minn=0.3,maxx=0.45)
        r_pattern = color_utils.cos(theta, offset=t/5, period=10, minn=0, maxx=1)
        #r,g,b = [r_pattern*item for item in (r,g,b)]  ###uncomment this line to add the spiral effect
        r, g, b = [color_utils.remap(color, 0, 1, 0, 255) for color in (r, g, b)]
    my_pixels.append((r, g, b))

def moons_spiral(t, coord, my_pixels, R_min, R_max, fps=100): ##this has the effect of just the outward moon spiraling slowly
    R = radius(coord)
    x, y, z = coord
    theta = find_theta(coord)
    R = color_utils.remap(R, R_min, R_max, 0, 6)
    if R > 5.5:
        r = color_utils.cos(theta, offset=t /10, period=12, minn=0, maxx=1)
        g = color_utils.cos(theta, offset=t / 10, period=12, minn=0, maxx=1)
        b = color_utils.cos(theta, offset=t / 10, period=12, minn=0, maxx=1)
        r, g, b = [color_utils.remap(color, 0, 1, 0, 255) for color in (r, g, b)]
    else:
        r,g,b = (20,20,10)
    my_pixels.append((r,g,b))

def rainbow_wave(t, coord, my_pixels, fps=100):
    x=coord[0]
    y=coord[1]
    z=coord[2]
    r = color_utils.cos(x, offset=t/8, period=10, minn=0, maxx=0.8)
    g = color_utils.cos(y, offset=t/8, period=10, minn=0, maxx=0.8)
    b = color_utils.cos(z, offset=t/8, period=10, minn=0, maxx=0.8)
    r, g, b = [color_utils.remap(color, 0, 1, 0, 255) for color in (r, g, b)]
    my_pixels.append((r,g,b))

def white_blinking(t, start_time, interval, coord, num_pixels ,my_pixels, fps=100):
    x,y,z=coord
    x=x+0.1
    # if t - start_time > interval / 2:
    #     x_new=y
    #     y_new=x
    #     y=y_new
    #     x=x_new
    r=color_utils.cos(x/y + y/z,offset=t/10,period=6,minn=0,maxx=0.4)
    g = color_utils.cos(x / y + y / z, offset=t / 10, period=6, minn=0, maxx=0.4)
    b = color_utils.cos(x / y + y / z, offset=t / 10, period=6, minn=0, maxx=0.4)
    color=(r,g,b)
    r,g,b=color_utils.gamma(color,0.5)
    r, g, b = [color_utils.remap(color, 0, 1, 0, 255) for color in (r, g, b)]
    my_pixels.append((r,g,b))


####specify location of layout file"

#layout='C:\Users\maayan.dermer\Downloads\InsomniacsServer-master\InsomniacsServer-master\layouts\insomniacs.json'

# Read in coordinates.
coordinates = []
for item in json.load(open(layout_json_path)):
    if 'point' in item:
        coordinates.append(tuple(item['point']))

num_pixels=len(coordinates)
R=[radius(coord) for coord in coordinates]
R_max=max(R)
R_min=min(R)


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
            if aniIndex == 0:
                outward_swell()
            if aniIndex == 1:
                raver_palid()
            if aniIndex == 2:
                play_rainbow()
            if aniIndex == 3:
                cone()
            if aniIndex == 4:
                counter_clockwise_rainbow()
            if aniIndex == 5:
                [moons_and_planets_blink(t,coord,my_pixels,R_min,R_max) for coord in coordinates]
            if aniIndex == 6:
                [rainbow_wave(t,coord,my_pixels) for ii,coord in enumerate(coordinates)]
            if aniIndex == 7:
                [white_blinking(t, start_time, interval, coord, num_pixels, my_pixels) for coord in coordinates]
            if aniIndex == 8:
                [moons_spiral(t,coord,my_pixels,R_min,R_max) for coord in coordinates]
            time.sleep(1)
            print (aniIndex)


# And write a function that chooses a different song randomly that gets called each time the SONG_END event is fired:
def play_a_different_song():
    global _currently_playing_song, _songs
    next_song = random.choice(_songs)
    while next_song == _currently_playing_song:
        next_song = random.choice(_songs)
    _currently_playing_song = next_song
    #print(str(_currently_playing_song) + " is played now...")
    pygame.mixer.music.load(next_song)
    pygame.mixer.music.play(1)


if __name__ == "__main__":
    music_path = 'C:\\Users\\maayan.dermer\\Downloads\\InsomniacsServer-master\\InsomniacsServer-master'
    
    if (run_sim == True):
        client = opc.Client('localhost:7890')
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
    #pygame.mixer.music.load('/home/maayand/Downloads/music/01 Aphelion.mp3')

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
                #print(str(_currently_playing_song) + " the song ended!")
                play_a_different_song()
        time.sleep(1)

    # freda() #0
    # raver_plaid() #1
    # play_rainbow() #2
    # cone() #3
    # counter_clockwise_rainbow() #4
