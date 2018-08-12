from node import Cluster
import time
import logging

all_nodes = Cluster (3,0.01)
all_nodes.start()



def main():
    i = 0
    while True:
        all_nodes.setNodeColor(0, i, 0, 0)
        all_nodes.setNodeColor(1, 0, i, 0)
        all_nodes.setNodeColor(2, 0, 0, i)

        i = i+1
        if i >= 255:
            i=0
        time.sleep(0.01)

if __name__ == "__main__":
    main()


