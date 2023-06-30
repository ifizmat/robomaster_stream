import cv2
import socket
import numpy as np
import time
import queue
import logging
import time
import libmedia_codec

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
    time.sleep(0.01)
    i+=1
    #print(f"i = {i}")
    if i>32:
      receiving = False
    try:
      if sock is None:
        break
      data, addr = sock.recvfrom(4096)
      if not receiving:
        break
      #print(f"recv_count = {recv_count}")
      recv_count = recv_count + 1
      if sock_queue.full():
        logger.warning("StreamConnection: _recv_task, sock_data_queue is full.")
        print("StreamConnection: _recv_task, sock_data_queue is full.")
        sock_queue.get()
      else:
        logger.debug("StreamConnection: _recv_task, recv {0}, len:{1}, data:{2}".format(
                      recv_count, len(data), data))
        #print("StreamConnection: _recv_task, recv {0}, len:{1}, data:{2}".format(
        #       recv_count, len(data), data))
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

def read_buf(timeout=2):
  try:
    buf = sock_queue.get(timeout=timeout)
    return buf
  except Exception as e:
    logger.warning("StreamConnection: read_buf, exception {0}".format(e))
    return None


while True:
  receiving = True
  _recv_task()
  i = sock_queue.qsize()
  print(f"qsize: {i}")

  data = b''
  while not sock_queue.empty():
    print("\n===\n===\n===\n")

    buf = read_buf()
    if buf:
      data += buf
    #print(f"\n\n\nget {i}: {data}")
    frames = libmedia_codec.H264Decoder().decode(data)
    #print(f"\n\n\nframes {i}: {frames}")
    print(f"frames len(): {len(frames)}")
    for frame_data in frames:
      (frame, width, height, ls) = frame_data
      #print(f"\n\n\nframes {i}: {data}")
    i -= 1
  """
  while not sock_queue.empty():
    print("\n===\n===\n===\n")
    print(f"\n\n\nget {i}: {sock_queue.get()}")
    i -= 1
  """
  time.sleep(1)

# Clean up resources
sock.close()
#cv2.destroyAllWindows()

