'''
entropy_engine.py
Processes F(X, Y) -> E, where F is some computation and X and Y are entropy sources to generate E, which is true random data stream.
'''

import redis
import numpy as np
import io
import threading

r = redis.Redis(host='localhost', port=6379, db=0)

def read_video_stream():
    last_video_id = '0-0'
    while True:
        response = r.xread({'video_data_stream': last_video_id}, block=1000, count=1)
        if response:
            stream, messages = response[0]
            for msg_id, msg_data in messages:
                last_video_id = msg_id
                img_binary = msg_data[b'frame']
                print('[VIDEO]', ' '.join(format(b, '08b') for b in img_binary[:32]))

def read_sdr_stream():
    last_sdr_id = '0-0'
    while True:
        response = r.xread({'sdr_data_stream': last_sdr_id}, block=1000, count=1)
        if response:
            stream, messages = response[0]
            for msg_id, msg_data in messages:
                last_sdr_id = msg_id
                iq_binary = msg_data[b'iq']
                print('[SDR]', ' '.join(format(b, '08b') for b in iq_binary[:32]))

def F(X, Y):
    # Placeholder for the actual function that combines X and Y to produce E
    E = (X + Y) % 256  # Example operation, replace with a more complex one
    return E

if __name__ == "__main__":
    # t1 = threading.Thread(target=read_video_stream, daemon=True)
    # t2 = threading.Thread(target=read_sdr_stream, daemon=True)
    # t1.start()
    # t2.start()
    # t1.join()
    # t2.join()
    read_sdr_stream()
    #read_video_stream()