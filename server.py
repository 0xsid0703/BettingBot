from flask import Flask
from flask_cors import CORS
import json
import argparse
import os

def main():

    parser = argparse.ArgumentParser(description="Horse Racing Server")
    parser.add_argument ("--start", help="RESP API Daemon Start", action="store_true")
    parser.add_argument ("--stop", help="RESP API Daemon Stop", action="store_true")
    args = parser.parse_args()
    
    if args.start:
        pid = os.fork()
        if pid > 0:
            from routers import api
            app = Flask(__name__)
            api.init_app(app)

            CORS(app, supports_credentials=True)
            app.config['CORS_HEADERS'] = 'Content-Type'
            app.config['CORS_RESOURCES'] = {r"*": {"origins": "*"}}

            global host, port
            host = "0.0.0.0"
            port = 5555
            try:
                with open("config/main.json") as f:
                    config = json.load(f)
                    host = config['host']
                    port = config['port']
            except Exception as e:
                print ("Config file read error.")

            app.run(host = host, port = port, debug = True)
            fd = open("./server-pid", "w"); fd.write (str(os.getpid())); fd.close()
    elif args.stop:
        os.chdir(os.getcwd())
        try:
            fd = os.popen("lsof -t -i:5555", "r"); pids = fd.readlines(); fd.close()
            for pid in pids:
                if len(pid.strip()) == 0: continue
                fd = os.popen ("kill %s" % pid.strip(), "r"); fd.close()
        except:
            fd = open ("./server-pid", "r"); pid = fd.read(); fd.close()
            fd = os.popen ("kill %s" % pid.strip(), "r"); fd.close()

if __name__ == '__main__':
    main ()
