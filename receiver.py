#!/usr/bin/env python

from __future__ import division

import socket
import struct

from cv2 import destroyAllWindows, imdecode, imshow, waitKey
from numpy import fromstring, uint8

MAX_DGRAM = 2 ** 16


def main():
    """ Getting image udp frame &
    concate before decode and output image """

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', 12345))
    dat = b''

    while True:
        seg, addr = sock.recvfrom(MAX_DGRAM)
        dat += seg[1:]

        if struct.unpack("B", seg[0:1])[0] >= 1:
            img = imdecode(fromstring(dat, dtype=uint8), 1)
            imshow('Frame', img)
            dat = b''

            if waitKey(1) & 0xFF == ord('q'):
                break

    # cap.release()
    destroyAllWindows()
    sock.close()


if __name__ == "__main__":
    main()
