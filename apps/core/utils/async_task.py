import threading
from functools import wraps
import sys
import logging

logger = logging.getLogger(__name__)

def run_in_background(func):
    """
    Decorator to run a function in a separate thread.
    Useful for offloading email sending or background tasks without blocking the main thread.
    Bypasses threading during tests to ensure synchronous test evaluation.
    Logs any unhandled exceptions that occur during execution.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'test' in sys.argv:
            return func(*args, **kwargs)
            
        def thread_target():
            try:
                func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in background task '{func.__name__}': {e}", exc_info=True)
                
        thread = threading.Thread(target=thread_target)
        thread.daemon = True
        thread.start()
        return thread
    return wrapper
