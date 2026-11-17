import threading
import time


def log_node(node: str, status: str, **details):
    """Print a timestamped status line with the thread, to check that the fan-out branches run in parallel."""
    extra = " | ".join(f"{k}={v}" for k, v in details.items())
    print(f"[{time.strftime('%H:%M:%S')}.{int(time.time() * 1000) % 1000:03d}] [{node}] [thread={threading.current_thread().name}] {status}" + (f" | {extra}" if extra else ""))
