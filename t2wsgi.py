# A quickie trial integration of geiger counter parts
import machine
import network
import ntptime
from g1 import Geiger, GLog, Gwsgi, GReportPeriodically
from ws2 import WS

class Thing:
    pass

ntptime.settime()
g = Thing()
g.uid = machine.unique_id()
g.wlan = network.WLAN()

geiger = Geiger()
glog = GLog(geiger)
grep = GReportPeriodically(g, glog)
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

"""
httpd = make_server('', 8000, demo_app)

print("Serving HTTP on port 8000...")

# Respond to requests until process is killed
httpd.serve_forever()

# Alternative: serve one request, then exit
httpd.handle_request()
"""
