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
    i=255
    # Send pixels forever

    print('    sending pixels forever (control-c to exit)...')
    print('')

    n_pixels = 25  # number of pixels in the included "wall" layout
    fps = 60  # frames per second

    # how many sine wave cycles are squeezed into our n_pixels
    # 24 happens to create nice diagonal stripes on the wall layout
    freq_r = 24
    freq_g = 24
    freq_b = 24

    # how many seconds the color sine waves take to shift through a complete cycle
    speed_r = 7
    speed_g = -13
    speed_b = 19

    start_time = time.time()

    while True:
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
    '''
    while True:
        in_pixel = input("Enter pixel number?")
        my_pixels = [(i, i, i), (i, i, i), (i, i, i), (i, i, i), (i, i, i),
                     (i, i, i), (i, i, i), (i, i, i), (i, i, i), (i, i, i),
                     (i, i, i), (i, i, i), (i, i, i), (i, i, i), (i, i, i),
                     (i, i, i), (i, i, i), (i, i, i), (i, i, i), (i, i, i),
                     (i, i, i), (i, i, i), (i, i, i), (i, i, i), (i, i, i)]
        #i=i+1
        #if i>=255:
        #    i=0

        for x in range(num_nodes):
            all_nodes.setNodeColor(x, i, i, i)
            my_pixels[x] = (i, i, i)

        my_pixels[int(in_pixel)] = (255, 0, 0)
        all_nodes.setNodeColor(int(in_pixel), 255, 0, 0)

        # random.shuffle(my_pixels)
        if client.put_pixels(my_pixels, channel=0):
            print
            'sent'
        else:
            print
            'not connected'
        time.sleep(0.01)
    '''
if __name__ == "__main__":
    main()


