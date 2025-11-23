'''
entropy_engine.py
Processes F(X, Y) -> E, where F is some computation and X and Y are entropy sources to generate E, which is true random data stream.
'''

import redis
import numpy as np
import io
import threading
import time
import hashlib

r = redis.Redis(host='localhost', port=6379, db=0)
duration = 1

def flush_redis_streams():
    try:
        r.delete('sdr_data_stream', 'video_data_stream')
        print("Flushed Redis streams")
    except Exception as e:
        print(f"Warning: Could not flush Redis: {e}")

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
                #print('[VIDEO]', binary_str)
    
    # binary string to integer
    if video_data:
        combined = ''.join(video_data)
        return int(combined, 2)
    return None

def read_sdr_stream():
    last_sdr_id = '$'  # Use '$' to read only NEW messages (not old ones)
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
                #print('[SDR]', binary_str)
    
    # binary string to integer
    if sdr_data:
        combined = ''.join(sdr_data)
        return int(combined, 2)
    return None

def bit_length(n):
    if n == 0:
        return 1
    return n.bit_length()

def truncate_to_decimal_length(hash_int, num_digits):
    """
    Truncate hash integer to a number with exactly num_digits decimal digits.
    
    Args:
        hash_int: Integer from hash
        num_digits: Desired number of decimal digits
    
    Returns:
        Integer with exactly num_digits decimal digits (e.g., 5 digits -> 10000-99999)
    """
    if num_digits <= 0:
        return 0
    
    # Define the range for the desired number of digits
    min_val = 10 ** (num_digits - 1)  # e.g., 10000 for 5 digits
    max_val = (10 ** num_digits) - 1   # e.g., 99999 for 5 digits
    range_size = max_val - min_val + 1
    
    # Map hash_int to the desired range
    result = (hash_int % range_size) + min_val
    
    return result

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
    lx = bit_length(x)
    ly = bit_length(y)
    
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
    result = truncate_to_decimal_length(hash_int, space)
    
    #print(f"Generated {space}-digit random number: {result}")
    
    return result

if __name__ == "__main__":
    # Flush old data before starting
    flush_redis_streams()
    counter = 0
    # t1 = threading.Thread(target=read_video_stream, daemon=True)
    # t2 = threading.Thread(target=read_sdr_stream, daemon=True)
    # t1.start()
    # t2.start()
    # t1.join()
    # t2.join()

    while True:
        x = read_sdr_stream()
        y = read_video_stream()
        space = 10

        randomNumber = F(x, y, space)
        counter+=1
        print(f"Generated Random Number {counter}: {randomNumber}")
