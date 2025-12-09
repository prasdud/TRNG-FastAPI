'''
entropy_engine.py
Processes F(X, Y) -> E, where F is some computation and X and Y are entropy sources to generate E, which is true random data stream.
'''

import redis
import time
import hashlib
import utils.helpers as helpers
import random

r = redis.Redis(host='localhost', port=6379, db=0)
duration = 1


def read_video_stream():
    last_video_id = '$'  # Use '$' to read only NEW messages (not old ones)
    video_data = []
    end_time = time.perf_counter() + duration
    
    while time.perf_counter() < end_time:
        response = r.xread({'video_data_stream': last_video_id}, block=1000, count=1)
        if response:
            stream, messages = response[0]
            for msg_id, msg_data in messages:
                last_video_id = msg_id
                img_binary = msg_data[b'frame']
                binary_str = ''.join(format(b, '08b') for b in img_binary[:32])
                video_data.append(binary_str)
    
    # binary string to integer
    if video_data:
        combined = ''.join(video_data)
        return int(combined, 2)
    return None

def read_sdr_stream():
    last_sdr_id = '$'
    sdr_data = []
    end_time = time.perf_counter() + duration
    
    while time.perf_counter() < end_time:
        response = r.xread({'sdr_data_stream': last_sdr_id}, block=1000, count=1)
        if response:
            stream, messages = response[0]
            for msg_id, msg_data in messages:
                last_sdr_id = msg_id
                iq_binary = msg_data[b'iq']
                binary_str = ''.join(format(b, '08b') for b in iq_binary[:32])
                sdr_data.append(binary_str)
    
    # binary string to integer
    if sdr_data:
        combined = ''.join(sdr_data)
        return int(combined, 2)
    return None


def F(x, y, space):
    """
    Combine entropy sources x and y to produce a random number.
    
    Args:
        x: First entropy source (integer)
        y: Second entropy source (integer)
        space: Number of decimal digits in output (e.g., 5 -> 10000-99999)
    
    Returns:
        Random number with exactly 'space' decimal digits
    """
    if x is None or y is None:
        print("Error: Invalid entropy sources (None values)")
        return None
    
    # Constants
    L = 64
    
    # Calculate bit lengths
    lx = helpers.bit_length(x)
    ly = helpers.bit_length(y)
    
    #print(f"x bit length: {lx}, y bit length: {ly}")
    
    # Construct E using bitwise operations
    # E = (lx << (L + ly + lx)) | (ly << (lx + L)) | (x << ly) | y
    E = (lx << (L + ly + lx)) | (ly << (lx + L)) | (x << ly) | y
    
    #print(f"Combined E: {E}")
    
    # Convert E to bytes for SHA256
    # Calculate the number of bytes needed
    e_bytes = E.to_bytes((E.bit_length() + 7) // 8, byteorder='big')
    
    # Hash with SHA256
    hash_result = hashlib.sha256(e_bytes).digest()
    
    # Convert hash to integer
    hash_int = int.from_bytes(hash_result, byteorder='big')
    
    # Truncate to desired decimal length
    result = helpers.truncate_to_decimal_length(hash_int, space)
    
    #print(f"Generated {space}-digit random number: {result}")
    
    return result

if __name__ == "__main__":
    helpers.flush_redis_streams(r)
    counter = 0


    while True:
        x_true_entropy_flag = True
        y_true_entropy_flag = True
    
        start_time_for_sdr = time.perf_counter()
        x = read_sdr_stream()
        end_time_for_sdr = time.perf_counter()
        
        start_time_for_video = time.perf_counter()
        y = read_video_stream()
        end_time_for_video = time.perf_counter()

        if x is None:
            x = random.getrandbits(256)
            x_true_entropy_flag = False
        if y is None:
            y = random.getrandbits(256)
            y_true_entropy_flag = False

        space = 10

        start_time_for_entropy_engine = time.perf_counter()
        randomNumber = F(x, y, space)
        end_time_for_entropy_engine = time.perf_counter()

        counter+=1

        if x_true_entropy_flag == False or y_true_entropy_flag == False:
            true_entropy_flag = False
        else:
            true_entropy_flag = True

        print(f"Generated Random Number {counter}: {randomNumber}\nTrue Entropy: {true_entropy_flag}\nIs SDR working?: {x_true_entropy_flag}\nIs Video working: {y_true_entropy_flag} ")
        print(f"Time taken for SDR stream: {end_time_for_sdr - start_time_for_sdr:.6f} seconds")
        print(f"Time taken for Video stream: {end_time_for_video - start_time_for_video:.6f} seconds")
        print(f"Time taken for Entropy Engine: {end_time_for_entropy_engine - start_time_for_entropy_engine:.6f} seconds")
        print("-"*69)