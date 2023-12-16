import os
import sys
from datetime import datetime
import argparse
import subprocess
import time

# def runStream():
    
#     while True:
#         process = subprocess.Popen ("/usr/bin/python3 ./stream.py", shell=True)
#         time.sleep (3600)
#         process.kill ()


def main():
    parser = argparse.ArgumentParser(description="Horse Racing Daemon")