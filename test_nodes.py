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
if __name__ == "__main__":
    main()


