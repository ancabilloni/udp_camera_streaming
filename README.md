# Fast camera live streaming with UDP

### Introduction

For camera live-streaming application over the computer network, TCP/IP or Transmission Control Protocol/Internet Protocol could come first as a reasonable choice. This method allows a large piece of information to be transmitted reliably, as it manages how a large packet being broken into smaller packets to be transmitted and reassembled in the right order at the the destination. [1]

Another famous network protocol is UDP or User Datagram Protocol. The implementation of this method is for fast data transmission (low-latency). However, UDP's drawback is less reliable compared to TCP/IP as there is always chance of data loss (packet drop). [2] UDP is structured in the way that not neccessarily implementing many of the control checks as in TCP/IP for the speed trade-off. From author's experience in using UDP, lossy is there but not always a concern in reliable network.

In this project, I'll explore live streaming over the network with UDP for speedy streaming.

### Pre-requisite
- Python 2 or 3
- OpenCV
- Numpy
- Socket
- Struct
- Webcam

### Image Frame Packaging

Explore the `sender.py` file.

The implementation are two steps. OpenCV library is being used to obtain image from wecam in `main()`, then passing `frame` into the `FrameSegment()` class to break down the frame and send over UDP. 

```
def main():
    """ Top level main function """
    # Set UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = 12345

    fs = FrameSegment(s, port)
    
    cap = cv2.VideoCapture(0)
    while (cap.isOpened()):
        _, frame = cap.read()
        fs.udp_frame(frame)
    cap.release()
    cv2.destroyAllWindows()
    s.close()
```

Something to note here is that the **encoding** and **decoding** feature in OpenCV being used to further compress the raw image size significantly but still maintaining decent image quality after decompress. 

After the raw frame is compressed, implementing `numpy`'s `tostring()` feature to convert the array into one-dimension bytes-array. The data packet sent by UDP is called **datagram**, the maximum limit of each datagram is **2^16 or 65536 bytes** with some bytes are reserved for header. To avoid data overflow and corrupt the codes, I do not use up to the maximum datagram's limit.

To determine the number of segments, I am using ceiling to round up the quotient of **bytearray_size/MAX_IMAGE_DGRAM**. Because `math.ceil` in Python2 is not rounding up natively as in Python3, so adding `from __future__ import division` helps to get this function to ceil up properly [3].

In this simple implementation, I use the first byte for current segment number which serves as a simple flag for the receiver to know whether there are still more segments of the image data coming or not. If the segment number is 1, this is the last data segment. Others are welcomed to try other flag/checksum method for more reliable check (for example: if a packet is dropped/never arrived, how the logic being handled?)

```
class FrameSegment(object):
    """ 
    Object to break down image frame segment
    if the size of image exceed maximum datagram size 
    """
    MAX_DGRAM = 2**16
    MAX_IMAGE_DGRAM = MAX_DGRAM - 64 # extract 64 bytes in case UDP frame overflown
    def __init__(self, sock, port, addr="127.0.0.1"):
        self.s = sock
        self.port = port
        self.addr = addr

    def udp_frame(self, img):
        """ 
        Compress image and Break down
        into data segments 
        """
        compress_img = cv2.imencode('.jpg', img)[1]
        dat = compress_img.tostring()
        size = len(dat)
        num_of_segments = math.ceil(size/(MAX_IMAGE_DGRAM))
        array_pos_start = 0
        while num_of_segments:
            array_pos_end = min(size, array_pos_start + MAX_IMAGE_DGRAM)
            self.s.sendto(struct.pack("B", num_of_segments) +
                dat[array_pos_start:array_pos_end], 
                (self.addr, self.port)
                )
            array_pos_start = array_pos_end
            num_of_segments -= 1
```

### Image Frame Decode

Explore the `receiver.py` file.
The logic on the receiver's end is simple. It is to reverse the process of the sender:
- Make sure to buffer out the current frame to make sure we are not starting in the middle of the segment stream.
- Gather and concate all data segments (using the segment number for logic).
- Using `numpy`'s `fromstring()` to convert the byte-array back to numpy array.
- Using `OpenCV`'s `imdecode` to decode the compressed numpy array back to numpy image.
- Lastly, display the image.

```
MAX_DGRAM = 2**16

def dump_buffer(s):
    """ Emptying buffer frame """
    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        print(seg[0])
        if struct.unpack("B", seg[0:1])[0] == 1:
            print("finish emptying buffer")
            break

def main():
    """ Getting image udp frame &
    concate before decode and output image """
    
    # Set up socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', 12345))
    dat = b''
    dump_buffer(s)

    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        if struct.unpack("B", seg[0:1])[0] > 1:
            dat += seg[1:]
        else:
            dat += seg[1:]
            img = cv2.imdecode(np.fromstring(dat, dtype=np.uint8), 1)
            cv2.imshow('frame', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            dat = b''

    # cap.release()
    cv2.destroyAllWindows()
    s.close()
```

### Result
Here is a quick screen record result.
https://www.youtube.com/watch?v=HctlRoi_RVA

### Reference 
1. https://searchnetworking.techtarget.com/definition/TCP-IP
2. https://searchnetworking.techtarget.com/definition/UDP-User-Datagram-Protocol
3. https://stackoverflow.com/a/17511341

### TO-DOs:
- Add C++ implementation
- Add javascript receiver implementation ?
