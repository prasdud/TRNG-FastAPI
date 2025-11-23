'''
video_service.py
Captures live video from a webcam for now and returns raw video data stream as BGR24 numpy arrays. (maybe flatten)
'''

import av
import cv2
import redis
from utils.logger import logger as log


container = av.open("/dev/video0") # 
r = redis.Redis(host='localhost', port=6379, db=0)


# There is a bottleneck here, a delay of 5 seconds in the video. need to figure out how to optimize this
# maybe use threading or multiprocessing or asyncio
# or maybe use a faster serialization method like msgpack or protobuf
# or maybe use a faster redis client like aioredis

for frame in container.decode(video=0):
    img = frame.to_ndarray(format='bgr24')      # raw numpy array of the frame

    img_binary = img.tobytes()                  # binary representation of the frame

    log.info('Video frame binary (first 32 bytes): ' + ' '.join(format(b, '08b') for b in img_binary[:32]))

    cv2.imshow('Video', img)
    # Add with MAXLEN to keep only last 100 entries (prevents memory explosion)
    r.xadd('video_data_stream', {'frame': img_binary}, maxlen=100, approximate=True)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
container.close()