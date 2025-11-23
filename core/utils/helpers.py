def flush_redis_streams(r):
    """
    Flush specified Redis streams to remove old data.
    Args:
        r: Redis client instance.
    """
    try:
        r.delete('sdr_data_stream', 'video_data_stream')
        print("Flushed Redis streams")
    except Exception as e:
        print(f"Warning: Could not flush Redis: {e}")


def bit_length(n):
    """
    Calculate the bit length of an integer n.
    Args:
        n: Integer to calculate bit length for.
    Returns:
        Bit length of n.
    """
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