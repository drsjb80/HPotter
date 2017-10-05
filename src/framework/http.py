import socket
from datetime import *


print "--" + datetime.now().strftime('%Y %b %d %H:%M:%S') + "--" , "http://www.ourserver.com/"
print "Resolving ourserver.com... " , (socket.gethostbyname(socket.gethostname()))
print "Connecting to ourserver.|" + (socket.gethostbyname(socket.gethostname())) +"|" +  "... connected"
print "HTTP request sent, awaiting response..."
print "  HTTP/1.1 200 OK"
print "  Date: ", datetime.now().strftime("%a, %d %b %y %H:%M:%S"), "GMT"
print "  Server: Apache/2.4.6 (Red Hat Enterprise Linux) OpenSSL/1.0.2k-fips mod_fcgid/2.3.9 PHP/5.4.16"
print "  Last-Modified: ", datetime.today().strftime("%a, %d %b %y %H:%M:%S"), "GMT"
print "  Accept-Ranges: bytes"
print "  Content-Length:", "44911"
print "  Cache-Control: max-age=0"
print "  Expires", datetime.today().strftime("%a, %d %b %y %H:%M:%S"), ",", "  Expires: ", datetime.today().strftime("%a, %d %b %y %H:%M:%S") + str(timedelta(hours=12))
print "  Keep-Alive: timeout=5, max=100"
print "  Connection: Keep-Alive"
print "  Content-Type: text/html; charset=UTF-8"
print " Length: 44911 (44k) [text/html]"