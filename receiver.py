#!/usr/bin/env python

from __future__ import division

import socket
import struct

import cv2
import numpy as np

MAX_DGRAM = 2 ** 16


def main():
    """ Getting image udp frame &
    concate before decode and output image """

    # Set up socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('localhost', 12345))
    dat = b''

    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)

        if struct.unpack("B", seg[0:1])[0] >= 1:
            dat += seg[1:]
            img = cv2.imdecode(np.fromstring(dat, dtype=np.uint8), 1)
            cv2.imshow('Frame', img)
            dat = b''

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # cap.release()
    cv2.destroyAllWindows()
    s.close()


if __name__ == "__main__":
    main()
