# A quickie trial integration of geiger counter parts
import machine
import micropython
import network
import ntptime
import time
from g1 import Geiger, GLog, Gwsgi, GReportPeriodically
from gu import update_bssids
from ws2 import WS

class Thing:
    pass

micropython.alloc_emergency_exception_buf(100)
time.time()                 # get time hooked up
try:
    ntptime.settime()
except:
    pass

g = Thing()
g.uid = machine.unique_id()
g.wlan = network.WLAN()
update_bssids(g)

geiger = Geiger()
glog = GLog(geiger)
grep = GReportPeriodically(g, glog, host='put.into.com')
gw = Gwsgi(glog)
ws = WS(gw.wsgi_app)

def start():
    geiger.start()
    glog.start()
    grep.start()
    run_ws()

def run_ws():
    ws.start()
    #ws.verbose = True
    print("ready")
    try:
        while True:
            ws.handle_one(10)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    finally:
        ws.stop()

def stop():
    ws.stop()
    grep.stop()
    glog.stop()
    geiger.stop()

def main():
    print("starting")
    start()

if __name__ == '__main__':
    main()

"""
httpd = make_server('', 8000, demo_app)

print("Serving HTTP on port 8000...")

# Respond to requests until process is killed
httpd.serve_forever()

# Alternative: serve one request, then exit
httpd.handle_request()
"""
