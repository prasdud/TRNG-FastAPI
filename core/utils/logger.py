import logging

_logger = None

def get_logger():
    global _logger
    if _logger is None:
        _logger = logging.getLogger("TRNG-FastAPI")
        _logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        _logger.addHandler(handler)
    return _logger

logger = get_logger()