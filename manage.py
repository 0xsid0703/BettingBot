import os
import time
from datetime import datetime, timedelta
import argparse
import subprocess


def main():

    parser = argparse.ArgumentParser(description="Horse Racing Server")
    parser.add_argument ("--start", help="FETCH and STREAM Daemon Start", action="store_true")
    parser.add_argument ("--stop", help="FETCH and STREAM Daemon Stop", action="store_true")
    args = parser.parse_args()

    if args.start:
        fd = open("./manage-pid", "w"); fd.write (str(os.getpid())); fd.close()
        while True:
            if datetime.now().hour in [22,23,0,1,2,3,4,5,6,7,8,9,10,11,12]:
                try:
                    fd = os.popen ("sudo systemctl stop horseracing-fetch"); fd.close()
                    fd = os.popen ("sudo systemctl stop horseracing-stream"); fd.close()
                except:
                    pass
                
                time.sleep (60)
                
                print ("Manage daemon start -----")
                fd = os.popen ("sudo systemctl start horseracing-fetch"); fd.close()
                fd = os.popen ("sudo systemctl start horseracing-stream"); fd.close()
                time.sleep (10800)
            else:
                try:
                    fd = os.popen ("sudo systemctl stop horseracing-fetch"); fd.close()
                    fd = os.popen ("sudo systemctl stop horseracing-stream"); fd.close()
                except:
                    pass
                time.sleep (900)
    
    elif args.stop:
        os.chdir(os.getcwd())
        fd = os.popen ("sudo systemctl stop horseracing-fetch"); fd.close()
        fd = os.popen ("sudo systemctl stop horseracing-stream"); fd.close()
        try:
            fd = open ("./manage-pid", "r"); pid = fd.read(); fd.close()
            fd = os.popen ("kill %s" % pid.strip(), "r"); fd.close()
        except:
            pass

if __name__ == "__main__":
    main()