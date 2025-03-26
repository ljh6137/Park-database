import time

def generate_timestamp():
    """生成以毫秒为单位的时间戳"""
    return int(time.time() * 1000)