import threading
from functools import wraps

def run_in_background(func):
    """
    Decorator to run a function in a separate thread.
    Useful for offloading email sending or background tasks without blocking the main thread.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    return wrapper
