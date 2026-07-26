import threading
from functools import wraps
import sys

def run_in_background(func):
    """
    Decorator to run a function in a separate thread.
    Useful for offloading email sending or background tasks without blocking the main thread.
    Bypasses threading during tests to ensure synchronous test evaluation.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'test' in sys.argv:
            return func(*args, **kwargs)
            
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    return wrapper
