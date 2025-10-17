'''
video_service.py
Captures live video from a webcam for now and returns raw video data stream as BGR24 numpy arrays. (maybe flatten)
'''

import av
import cv2
import numpy as np
import redis
import io

container = av.open("/dev/video0") # Adjust the path as necessary for your video source
r = redis.Redis(host='localhost', port=6379, db=0)


# There is a bottleneck here, a delay of 5 seconds in the video. need to figure out how to optimize this
# maybe use threading or multiprocessing or asyncio
# or maybe use a faster serialization method like msgpack or protobuf
# or maybe use a faster redis client like aioredis

for frame in container.decode(video=0):
    img = frame.to_ndarray(format='bgr24')      # raw numpy array of the frame

    # Get binary equivalent of the frame
    img_binary = img.tobytes()                  # binary representation of the frame

    # Print binary representation of each byte (first 32 bytes for brevity)
    print(' '.join(format(b, '08b') for b in img_binary[:32]))

    cv2.imshow('Video', img)
    r.publish('video_data_stream', img_binary)  # publish binary data to redis channel

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
container.close()