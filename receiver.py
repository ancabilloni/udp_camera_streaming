#!/usr/bin/env python

from __future__ import division

from socket import AF_INET, SOCK_DGRAM, socket
from struct import unpack

from cv2 import destroyAllWindows, imdecode, imshow, waitKey
from numpy import frombuffer, uint8


def main():
    """ Getting image udp frame &
    concate before decode and output image """

    MAX_DGRAM = 2 ** 16
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(('localhost', 12345))
    dat = b''

    while True:
        seg, addr = sock.recvfrom(MAX_DGRAM)
        dat += seg[1:]

        if unpack("B", seg[0:1])[0] >= 1:
            img = imdecode(frombuffer(dat, dtype=uint8), 1)
            imshow('Frame', img)
            dat = b''

            if waitKey(1) & 0xFF == ord('q'):
                break

    # cap.release()
    destroyAllWindows()
    sock.close()


if __name__ == "__main__":
    main()
