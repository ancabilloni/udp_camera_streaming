#!/usr/bin/env python

from __future__ import division

from math import ceil
from socket import AF_INET, SOCK_DGRAM, socket
from struct import pack

from cv2 import IMWRITE_JPEG_QUALITY, VideoCapture, destroyAllWindows, imencode


class FrameSegment(object):
    """
    Object to break down image frame segment
    if the size of image exceed maximum datagram size
    """
    MAX_DGRAM = 2 ** 16

    # extract 64 bytes in case UDP frame overflown
    MAX_IMAGE_DGRAM = MAX_DGRAM - 64

    def __init__(self, port=12345, remote='127.0.0.1', quality=100):
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.quality = [
            int(IMWRITE_JPEG_QUALITY), quality
        ]
        self.port = port
        self.addr = remote

    def udp_frame(self, img):
        """
        Compress image and Break down
        into data segments
        """

        compress_img = imencode(
            '.jpg', img, self.quality
        )[1]
        dat = compress_img.tobytes()
        size = len(dat)
        count = ceil(size / self.MAX_IMAGE_DGRAM)
        start = 0

        while count:
            end = min(
                size, start + self.MAX_IMAGE_DGRAM
            )
            self.sock.sendto(
                pack("B", count) + dat[start:end],
                (
                    self.addr,
                    self.port
                )
            )
            start = end
            count -= 1

    def quit(self, *largs):
        self.sock.close()


def main():
    """ Top level main function """

    remote = '127.0.0.1'
    port = 12345
    quality = 50

    fs = FrameSegment(port, remote, quality)
    cap = VideoCapture(2)

    while (cap.isOpened()):
        ret, frame = cap.read()

        # if frame is read correctly
        if ret:
            fs.udp_frame(frame)

    cap.release()
    destroyAllWindows()
    fs.quit()


if __name__ == "__main__":
    main()
