import socket
from datetime import *

# def time():
#     time = datetime.time() + datetime.date()

#def http_response():
#ip = socket.gethostbyname(socket.AF_INET)


print "--" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "--" , "http://www.ourserver.com/"
print "Resolving ourserver.com... " , (socket.gethostbyname(socket.gethostname()))
print "Connecting to ourserver.|" + (socket.gethostbyname(socket.gethostname())) +"|" +  "... connected"
print "HTTP request sent, awaiting response..."
print "  HTTP/1.1 200 OK"
print "  Date: ", datetime.now()
print "  Server: Apache/2.4.6 (Red Hat Enterprise Linux) OpenSSL/1.0.2k-fips mod_fcgid/2.3.9 PHP/5.4.16"
print "  Last-Modified: "
print "  Accept-Ranges: bytes"
print "  Content-Length:"
print "  Cache-Control: max-age=0"
print " ", datetime.today() , ",", "  Expires: " , datetime.now() + timedelta(hours=12)
print "  Keep-Alive: timeout=5, max=100"
print "  Connection: Keep-Alive"
print "  Content-Type: text/html; charset=UTF-8"
print "Length: "
print "Saving to: 'index.html        100%[===============================================>] 43.94K  --.-KB/s   in 0s"