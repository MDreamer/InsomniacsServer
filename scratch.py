import threading
import time
import logging
import socket

#logging.basicConfig(filename='central_spike.log', level=logging.INFO, format='%(asctime)s %(message)s',
#                    datefmt='%d/%m/%Y %I:%M:%S %p')


class Cluster(threading.Thread):
    def __init__(self, numNodes, refRate, MCAST_GRP = "192.168.1.255", MCAST_PORT = 4210):
        threading.Thread.__init__(self)
        self.numNodes = numNodes
        self.refRate = refRate  #refRate in Hz -> to ms(s) while in the loop
        self.MCAST_GRP = MCAST_GRP
        self.MCAST_PORT = MCAST_PORT
        self.dataSocket = bytearray([0] * (self.numNodes * 3)) #array or rgb node, x3 is for the rgb
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    #set a node to an RGB color
    def setNodeColor(self, nodeNum, red, green, blue):
        if (nodeNum < 0) or (nodeNum >= self.numNodes):
            logging.critical(nodeNum + ' is invalid node number')
            return

        if (red < 0) or (red > 255) or (green < 0) or (green > 255) or (blue < 0) or (blue > 255):
            logging.critical('Invalid color on node number ' + nodeNum + ' color could be only 0-255')
            return

        self.dataSocket[nodeNum*3] = red;
        self.dataSocket[(nodeNum*3)+1] = green;
        self.dataSocket[(nodeNum*3)+2] = blue;

    def run(self):
        self.loopDataCluster()

    def senddatasocket(self):
        self.sock.sendto(self.dataSocket, (self.MCAST_GRP, self.MCAST_PORT))
        print('sending data ' + str(self.dataSocket))

    # loop thread
    def loopDataCluster(self):
        while True:
            try:
                logging.debug('sending data to nodes')
                self.senddatasocket()
                time.sleep(self.refRate)
            except Exception as e:
                logging.critical(str(e) + ' cannot send data to cluster')
                time.sleep(self.refRate)