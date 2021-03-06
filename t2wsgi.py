# A quickie trial integration of geiger counter parts
import machine
import micropython
import network
import ntptime
from g1 import Geiger, GLog, Gwsgi, GReportPeriodically
from gu import update_bssids
from ws2 import WS

class Thing:
    pass

micropython.alloc_emergency_exception_buf(100)
g = Thing()

def main():
    ntptime.settime()
    g.uid = machine.unique_id()
    g.wlan = network.WLAN()
    update_bssids(g)

    geiger = Geiger()
    glog = GLog(geiger)
    grep = GReportPeriodically(g, glog, host='put.into.com')
    gw = Gwsgi(glog)
    ws = WS(gw.wsgi_app)
    print("ready to start")
    geiger.start()
    glog.start()
    grep.start()
    ws.start()
    #ws.verbose = True
    try:
        while True:
            ws.handle_one(10)
    except Exception as e:
        print(e)
        ws.stop()

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
