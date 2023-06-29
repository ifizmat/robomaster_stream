import cv2
import socket
import numpy as np
import time
import queue
import logging
import time

logger_name = "sdk"
logger = logging.getLogger(logger_name)
logger.setLevel(logging.INFO)

TCP_IP = '192.168.2.1' # Replace with the IP address of your robot
TCP_PORT = 40921

# Open a TCP socket and connect to the robot's video stream
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((TCP_IP, TCP_PORT))

# Start reading video stream data and displaying in a window
img_arr = bytearray()
img = None
receiving = True
recv_count = 0
sock_queue = queue.Queue(32)

def _recv_task():
  global recv_count
  #print("Called recv_task!!!\n\n\n")
  receiving = True
  logger.info("StreamConnection: _recv_task, Start to receiving Data...")
  print("StreamConnection: _recv_task, Start to receiving Data...")
  i = 0
  while receiving:
    time.sleep(1)
    i+=1
    print(f"i = {i}")
    if i>5:
      receiving = False
    try:
      if sock is None:
        break
      data, addr = sock.recvfrom(4096)
      if not receiving:
        break
      print(f"recv_count = {recv_count}")
      recv_count = recv_count + 1
      if sock_queue.full():
        logger.warning("StreamConnection: _recv_task, sock_data_queue is full.")
        print("StreamConnection: _recv_task, sock_data_queue is full.")
        sock_queue.get()
      else:
        logger.debug("StreamConnection: _recv_task, recv {0}, len:{1}, data:{2}".format(
                      recv_count, len(data), data))
        print("StreamConnection: _recv_task, recv {0}, len:{1}, data:{2}".format(
               recv_count, len(data), data))
        sock_queue.put(data)

    except socket.timeout:
      logger.warning("StreamConnection: _recv_task， recv data timeout!")
      print("StreamConnection: _recv_task， recv data timeout!")
      continue
    except Exception as e:
      logger.error("StreamConnection: recv, exceptions:{0}".format(e))
      print("StreamConnection: recv, exceptions:{0}".format(e))
      receiving = False
      return 

while True:
  receiving = True
  _recv_task()
  time.sleep(1);

# Clean up resources
sock.close()
#cv2.destroyAllWindows()

