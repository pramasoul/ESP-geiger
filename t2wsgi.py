# test
from g1 import Geiger, GLog, Gwsgi
from ws2 import WS
#from test_wsgi import s2_app

g = Geiger()
gl = GLog(g)
gw = Gwsgi(gl)
ws = WS(gw.wsgi_app)
print("ready to start")
ws.start()
ws.verbose = False
try:
    while True:
        ws.handle_one(10)
except:
    ws.stop()

"""
httpd = make_server('', 8000, demo_app)

print("Serving HTTP on port 8000...")

# Respond to requests until process is killed
httpd.serve_forever()

# Alternative: serve one request, then exit
httpd.handle_request()
"""
