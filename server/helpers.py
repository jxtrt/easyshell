import time

def is_device_still_alive(last_heartbeat_timestamp, timeout=60):
    return (time.time() - last_heartbeat_timestamp) < timeout