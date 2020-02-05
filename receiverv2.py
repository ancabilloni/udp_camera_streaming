#!/usr/bin/env python3

from __future__ import division
import cv2
import numpy as np
import socket
import struct

MAX_DGRAM = 1460 #2**16
start=0

def dump_buffer(s):
    """ Emptying buffer frame """
    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        if (len(seg[start:])) < MAX_DGRAM:
            print("finish emptying buffer")
            break

def main():
    """ Getting image udp frame &
    concate before decode and output image """
    
    # Set up socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('0.0.0.0', 11111))
    dat = b''
    dump_buffer(s)

    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        if len(seg[start:]) == MAX_DGRAM:    
            dat += seg[start:]
        elif len(seg[start:]) < MAX_DGRAM:
            dat += seg[start:]

            img = cv2.imdecode(np.frombuffer(dat, dtype=np.uint8),1)
            cv2.imshow('Receiver', img)
            dat = b''
            
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
           

    # cap.release()
    cv2.destroyAllWindows()
    s.close()

if __name__ == "__main__":
    main()
