'''
entropy_engine.py
Processes F(X, Y) -> E, where F is some computation and X and Y are entropy sources to generate E, which is true random data stream.
'''

import redis
import numpy as np
import io

r = redis.Redis(host='localhost', port=6379, db=0)
pubsub = r.pubsub()
pubsub.subscribe('video_data_stream')

for message in pubsub.listen():
    if message['type'] == 'message':
        buffer = io.BytesIO(message['data'])
        frame = np.load(buffer)  # deserializing bytes back to numpy array
        print(frame)