"""
from API.memory import print_memory
"""
import psutil
import os

_red_ = "\033[91m%s\033[00m"
_blue_ = "\033[94m%s\033[00m"
_yellow_ = "\033[93m%s\033[00m"


def print_memory_old():
    usage = psutil.Process(os.getpid()).memory_info().rss
    print(_yellow_ % f'memory usage: psutil {usage / 1024 / 1024} MB')

def print_memory():
    yellow, purple = "\033[93m%s\033[00m", "\033[95m%s\033[00m"

    usage = psutil.Process(os.getpid()).memory_info().rss
    usage = usage / 1024 // 1024

    print(yellow % "Memory usage:", purple % f"{usage} MB")
